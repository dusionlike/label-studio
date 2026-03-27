import io
import os
import uuid
import zipfile
from pathlib import PurePosixPath

from PIL import Image
from rest_framework.exceptions import ValidationError
import yaml

IMAGE_EXTENSIONS = {'.bmp', '.gif', '.jpg', '.jpeg', '.png', '.webp'}
YOLO_CONFIG_NAMES = ('data.yaml', 'data.yml')


def is_yolov8_zip(archive: zipfile.ZipFile) -> bool:
    members = [_normalize_zip_path(name) for name in archive.namelist() if not name.endswith('/')]

    has_dataset_config = any(os.path.basename(member).lower() in YOLO_CONFIG_NAMES for member in members)
    has_images_dir = any(member.startswith('images/') or '/images/' in member for member in members)
    has_labels_dir = any(member.startswith('labels/') or '/labels/' in member for member in members)

    return has_dataset_config and has_images_dir and has_labels_dir


def get_yolov8_class_names(archive: zipfile.ZipFile):
    config_member = _find_dataset_config(archive)
    dataset_config = yaml.safe_load(archive.read(config_member)) or {}

    return _parse_class_names(dataset_config.get('names'))


def load_yolov8_tasks(
    archive: zipfile.ZipFile,
    image_field_name: str,
    control_name: str,
    save_image,
    configured_labels=None,
):
    config_member = _find_dataset_config(archive)
    dataset_root = PurePosixPath(config_member).parent
    dataset_config = yaml.safe_load(archive.read(config_member)) or {}
    class_names = _parse_class_names(dataset_config.get('names'))
    _validate_configured_labels(class_names, configured_labels)
    image_members = _collect_image_members(archive, dataset_root, dataset_config)

    if not image_members:
        raise ValidationError('YOLOv8 ZIP 中没有找到可导入的图片文件。')

    tasks = []

    for image_member in image_members:
        image_bytes = archive.read(image_member)
        image_width, image_height = _read_image_size(image_member, image_bytes)
        image_url = save_image(os.path.basename(image_member), image_bytes)
        annotations = _load_image_annotations(
            archive=archive,
            image_member=image_member,
            image_width=image_width,
            image_height=image_height,
            class_names=class_names,
            control_name=control_name,
            image_field_name=image_field_name,
        )

        task = {
            'data': {
                image_field_name: image_url,
            }
        }

        if annotations:
            task['annotations'] = [{'result': annotations, 'ground_truth': True}]

        tasks.append(task)

    return tasks


def _validate_configured_labels(class_names, configured_labels):
    if not configured_labels:
        return

    configured_labels_set = {label for label in configured_labels if label}
    missing_labels = [label for label in class_names if label not in configured_labels_set]

    if missing_labels:
        missing_labels_text = '、'.join(missing_labels)
        raise ValidationError(
            f'YOLOv8 ZIP 中的类别 {missing_labels_text} 未在当前项目的 RectangleLabels 标签配置中定义。'
        )


def _find_dataset_config(archive: zipfile.ZipFile) -> str:
    for member in archive.namelist():
        normalized = _normalize_zip_path(member)
        if normalized and os.path.basename(normalized).lower() in YOLO_CONFIG_NAMES:
            return normalized

    raise ValidationError('YOLOv8 ZIP 中缺少 data.yaml 配置文件。')


def _parse_class_names(raw_names):
    if isinstance(raw_names, list):
        class_names = [str(name) for name in raw_names]
    elif isinstance(raw_names, dict):
        class_names = [str(name) for _, name in sorted(raw_names.items(), key=lambda item: int(item[0]))]
    else:
        raise ValidationError('YOLOv8 ZIP 中的 data.yaml 缺少 names 类别映射。')

    if not class_names:
        raise ValidationError('YOLOv8 ZIP 中的 names 类别映射不能为空。')

    return class_names


def _collect_image_members(archive: zipfile.ZipFile, dataset_root: PurePosixPath, dataset_config):
    prefixes = []

    for split_name in ('train', 'val', 'test'):
        split_path = dataset_config.get(split_name)

        if isinstance(split_path, str):
            resolved = _resolve_member_path(dataset_root, split_path)

            if os.path.splitext(resolved)[1]:
                continue

            prefixes.append(resolved.rstrip('/'))

    if not prefixes:
        prefixes.append(_resolve_member_path(dataset_root, 'images').rstrip('/'))

    members = []
    for member in archive.namelist():
        normalized = _normalize_zip_path(member)

        if not normalized or normalized.endswith('/'):
            continue
        if os.path.splitext(normalized)[1].lower() not in IMAGE_EXTENSIONS:
            continue
        if any(normalized == prefix or normalized.startswith(f'{prefix}/') for prefix in prefixes):
            members.append(normalized)

    if members:
        return sorted(set(members))

    fallback_members = []
    for member in archive.namelist():
        normalized = _normalize_zip_path(member)

        if not normalized or normalized.endswith('/'):
            continue
        if os.path.splitext(normalized)[1].lower() not in IMAGE_EXTENSIONS:
            continue
        if normalized.startswith('images/') or '/images/' in normalized:
            fallback_members.append(normalized)

    return sorted(set(fallback_members))


def _read_image_size(image_member: str, image_bytes: bytes):
    try:
        with Image.open(io.BytesIO(image_bytes)) as image:
            return image.size
    except Exception as exc:
        raise ValidationError(f'无法读取图片尺寸：{image_member}，错误：{exc}')


def _load_image_annotations(
    archive: zipfile.ZipFile,
    image_member: str,
    image_width: int,
    image_height: int,
    class_names,
    control_name: str,
    image_field_name: str,
):
    label_member = _guess_label_member(image_member)

    if label_member not in {_normalize_zip_path(name) for name in archive.namelist()}:
        return []

    label_content = archive.read(label_member).decode('utf-8')
    annotations = []

    for line_number, raw_line in enumerate(label_content.splitlines(), start=1):
        line = raw_line.strip()

        if not line:
            continue

        parts = line.split()
        if len(parts) != 5:
            raise ValidationError(
                f'YOLOv8 ZIP 目前只支持目标检测边界框格式，文件 {label_member} 第 {line_number} 行格式无效。'
            )

        try:
            class_index = int(float(parts[0]))
            x_center, y_center, width, height = [float(value) for value in parts[1:]]
        except ValueError as exc:
            raise ValidationError(f'YOLO 标签解析失败：{label_member} 第 {line_number} 行，错误：{exc}')

        if class_index < 0 or class_index >= len(class_names):
            raise ValidationError(f'YOLO 类别索引超出范围：{label_member} 第 {line_number} 行。')

        x = max(0.0, (x_center - width / 2) * 100)
        y = max(0.0, (y_center - height / 2) * 100)
        box_width = min(width * 100, 100 - x)
        box_height = min(height * 100, 100 - y)

        annotations.append(
            {
                'id': uuid.uuid4().hex[:10],
                'from_name': control_name,
                'to_name': image_field_name,
                'type': 'rectanglelabels',
                'origin': 'manual',
                'image_rotation': 0,
                'original_width': image_width,
                'original_height': image_height,
                'value': {
                    'x': x,
                    'y': y,
                    'width': box_width,
                    'height': box_height,
                    'rotation': 0,
                    'rectanglelabels': [class_names[class_index]],
                },
            }
        )

    return annotations


def _guess_label_member(image_member: str) -> str:
    image_path = PurePosixPath(image_member)
    image_stem = image_path.with_suffix('.txt')
    parts = list(image_stem.parts)

    for index, part in enumerate(parts):
        if part == 'images':
            parts[index] = 'labels'
            return _normalize_zip_path(str(PurePosixPath(*parts)))

    return _normalize_zip_path(str(image_stem))


def _resolve_member_path(dataset_root: PurePosixPath, relative_path: str) -> str:
    path = relative_path.replace('\\', '/').strip()
    pure_path = PurePosixPath(path)

    if pure_path.is_absolute():
        return _normalize_zip_path(str(pure_path.relative_to('/')))

    return _normalize_zip_path(str(dataset_root / pure_path))


def _normalize_zip_path(path: str) -> str:
    parts = []
    for part in path.replace('\\', '/').split('/'):
        if not part or part == '.':
            continue
        if part == '..':
            if parts:
                parts.pop()
            continue
        parts.append(part)
    return '/'.join(parts)