"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license."""

import copy
import io
import zipfile

import pytest
import requests_mock
import ujson as json
from data_import.models import FileUpload
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from projects.models import Project
from rest_framework.authtoken.models import Token
from tasks.models import Annotation, Prediction, Task


def post_data_as_format(setup, format_type, body, archive, multiply_files):
    # post as data
    if format_type == 'json_data':
        return setup.post(setup.urls.task_bulk, data=body, content_type='application/json')

    # post as files
    if format_type == 'json_file':
        files = {f'upload_file{i}.json': io.StringIO(body) for i in range(0, multiply_files)}
    elif format_type == 'csv_file':
        files = {f'upload_file{i}.csv': io.StringIO(body) for i in range(0, multiply_files)}
    elif format_type == 'tsv_file':
        files = {f'upload_file{i}.tsv': io.StringIO(body) for i in range(0, multiply_files)}
    elif format_type == 'txt_file':
        files = {f'upload_file{i}.txt': io.StringIO(body) for i in range(0, multiply_files)}
    else:
        raise Exception('Incorrect task data format to post')

    # zip: take files below and zip them
    if 'zip' in archive:
        file = io.BytesIO()
        ref = zipfile.ZipFile(file, mode='w', compression=zipfile.ZIP_DEFLATED)
        [ref.writestr(name, body.read()) for name, body in files.items()]

        ref.close()
        file.seek(0, 0)
        files = {'upload_file.zip': file}

        # replicate zip file x2
        if 'zip_x2' == archive:
            files.update({'upload_file2.zip': copy.deepcopy(file)})

    return setup.post(setup.urls.task_bulk, files)


@pytest.mark.parametrize('multiply_files', [1, 5])
@pytest.mark.parametrize('format_type', ['json_file', 'json_data'])
@pytest.mark.parametrize(
    'tasks, status_code, task_count',
    [
        ([{'data': {'dialog': 'some'}}], 201, 1),
        ([{'data': {'dialog': 'some'}}] * 10, 201, 10),
        ([{'data': {'another_field': 'some', 'dialog': 'some'}}], 201, 1),
        ([{'data': {'dialog': 123}, 'created_at': 123}], 201, 1),
        ([{'data': {'another_field': 'some'}}] * 10, 400, 0),
        ([{'data': {}}], 400, 0),
        ([{'data': None}], 400, 0),
        (None, 400, 0),
        ([{'data': 'string'}], 400, 0),
        ([{}, {}], 400, 0),
        ([{}], 400, 0),
        ({}, 400, 0),
        ([], 400, 0),
        ([{'dialog': 'some'}] * 10, 201, 10),
        ({'dialog': 'some'}, 201, 1),
        ([{'dialog': 'some', 'second_field': 123}] * 10, 201, 10),
        ([{'none': 'some', 'second_field': 123}] * 10, 400, 0),
    ],
)
@pytest.mark.django_db
def test_json_task_upload(setup_project_dialog, format_type, tasks, status_code, task_count, multiply_files):
    """Upload JSON as file and data with one task to project.
    Decorator pytest.mark.django_db means it will be clean DB setup_project_dialog for this test.
    """
    if format_type == 'json_data' and multiply_files > 1:
        pytest.skip('Senseless parameter combination')

    r = post_data_as_format(setup_project_dialog, format_type, json.dumps(tasks), 'none', multiply_files)
    print(f'Create json {format_type} tasks result:', r.content)
    assert r.status_code == status_code, f'Upload tasks failed. Response data: {r.data}'
    assert Task.objects.filter(project=setup_project_dialog.project.id).count() == task_count * multiply_files


@pytest.mark.parametrize(
    'tasks, status_code, task_count, annotation_count',
    [
        ([{'data': {'dialog': 'Test'}, 'annotations': [{'result': [{'id': '123'}]}]}] * 10, 201, 10, 10),
        (
            [{'data': {'dialog': 'Test'}, 'annotations': [{'result': [{'id': '123'}], 'ground_truth': True}]}],
            201,
            1,
            1,
        ),
        ([{'data': {'dialog': 'Test'}, 'annotations': [{'result': '123'}]}], 400, 0, 0),
        ([{'data': {'dialog': 'Test'}, 'meta': 'test'}] * 10, 400, 0, 0),
        ([{'data': {'dialog': 'Test'}, 'annotations': 'test'}] * 10, 400, 0, 0),
        ([{'data': {'dialog': 'Test'}, 'annotations': [{'trash': '123'}]}] * 10, 400, 0, 0),
    ],
)
@pytest.mark.django_db
def test_json_task_annotation_and_meta_upload(setup_project_dialog, tasks, status_code, task_count, annotation_count):
    """Upload JSON task with annotation to project"""
    format_type = 'json_file'
    multiply_files = 1

    r = post_data_as_format(setup_project_dialog, format_type, json.dumps(tasks), 'none', multiply_files)
    print('Create json tasks with annotations result:', r.content)
    assert r.status_code == status_code, 'Upload one task with annotation failed'

    # tasks
    tasks_db = Task.objects.filter(project=setup_project_dialog.project.id)
    assert tasks_db.count() == task_count * multiply_files
    for task in tasks_db:
        assert task.is_labeled, 'Task should be labeled'

    # annotations
    annotations = Annotation.objects.filter(task__project=setup_project_dialog.project.id)
    assert annotations.count() == annotation_count * multiply_files
    for i, annotation in enumerate(annotations):
        assert annotation.ground_truth


@pytest.mark.parametrize(
    'tasks, status_code, task_count, prediction_count',
    [
        (
            [
                {
                    'data': {'dialog': 'Test'},
                    'predictions': [
                        {
                            'result': [
                                {
                                    'id': '123',
                                    'from_name': 'answer',
                                    'to_name': 'dialog',
                                    'type': 'textarea',
                                    'value': {'text': ['Test prediction']},
                                }
                            ],
                            'model_version': 'test',
                        }
                    ],
                }
            ],
            201,
            1,
            1,
        ),
        ([{'data': {'dialog': 'Test'}, 'predictions': [{'WRONG_FIELD': '123'}]}], 400, 0, 0),
    ],
)
@pytest.mark.django_db
def test_json_task_predictions(setup_project_dialog, tasks, status_code, task_count, prediction_count):
    """Upload JSON task with predictions to project"""
    r = post_data_as_format(setup_project_dialog, 'json_file', json.dumps(tasks), 'none', 1)
    assert r.status_code == status_code, 'Upload one task with prediction failed'

    # predictions
    predictions = Prediction.objects.filter(project=setup_project_dialog.project.id)
    assert predictions.count() == prediction_count
    for i, predictions in enumerate(predictions):
        assert predictions.model_version == 'test'


@pytest.mark.parametrize('multiply_files', [1, 5])
@pytest.mark.parametrize('archive', ['none'])
@pytest.mark.parametrize('format_type', ['json_file'])
@pytest.mark.parametrize(
    'tasks, status_code, task_count, annotation_count',
    [
        (
            [{'data': {'dialog': 'Test'}, 'annotations': [{'result': [{'id': '123'}]}, {'result': [{'id': '456'}]}]}]
            * 10,
            201,
            10,
            20,
        ),
        ([{'data': {'dialog': 'Test'}, 'annotations': [{'trash': '123'}]}] * 10, 400, 0, 0),
    ],
)
@pytest.mark.django_db
def test_archives(
    setup_project_dialog, format_type, tasks, status_code, task_count, annotation_count, archive, multiply_files
):
    """Upload JSON task with annotation to project"""
    multiplier = (2 if 'zip_x2' == archive else 1) * multiply_files

    r = post_data_as_format(setup_project_dialog, format_type, json.dumps(tasks), archive, multiply_files)
    print('Create json tasks with annotations result:', r.content)
    assert r.status_code == status_code, 'Upload one task with annotation failed'

    # tasks
    tasks = Task.objects.filter(project=setup_project_dialog.project.id)
    assert tasks.count() == task_count * multiplier
    for task in tasks:
        assert task.is_labeled, 'Task should be labeled'

    # annotations
    annotations = Annotation.objects.filter(task__project=setup_project_dialog.project.id)
    assert annotations.count() == annotation_count * multiplier
    for annotation in annotations:
        assert annotation.ground_truth


@pytest.mark.parametrize('multiply_files', [1, 5])
@pytest.mark.parametrize('archive', ['none'])
@pytest.mark.parametrize('format_type', ['csv_file', 'tsv_file'])
@pytest.mark.parametrize(
    'tasks, status_code, task_count',
    [
        ('dialog,second\ndialog 1,second 1\ndialog 2,second 2', 201, 2),
        ('dialog,second,class\ndialog 1, second 2, class 1', 201, 1),
        ('here_is_error_in_column_count,second\ndialog 1, second 1, class 1', 400, 0),
        ('empty_rows\n', 400, 0),
        ('', 400, 0),
    ],
)
@pytest.mark.django_db
def test_csv_tsv_task_upload(
    setup_project_dialog, format_type, tasks, status_code, task_count, archive, multiply_files
):
    """Upload CSV/TSV with one task to project"""
    multiplier = (2 if 'zip_x2' == archive else 1) * multiply_files

    tasks = tasks if format_type == 'csv_file' else tasks.replace(',', '\t')  # prepare tsv file from csv
    r = post_data_as_format(setup_project_dialog, format_type, tasks, archive, multiply_files)
    print(f'Create {format_type} tasks result:', r.content)

    assert r.status_code == status_code, f'Upload one task {format_type} failed. Response data: {r.data}'
    assert Task.objects.filter(project=setup_project_dialog.project.id).count() == task_count * multiplier


@pytest.mark.parametrize('multiply_files', [1, 5])
@pytest.mark.parametrize('format_type', ['txt_file'])
@pytest.mark.parametrize('tasks, status_code, task_count', [('my text 1\nmy text 2\nmy text 3', 201, 3), ('', 400, 0)])
@pytest.mark.django_db
def test_txt_task_upload(setup_project_dialog, format_type, tasks, status_code, task_count, multiply_files):
    """Upload CSV/TSV with one task to project"""
    multiplier = multiply_files

    r = post_data_as_format(setup_project_dialog, format_type, tasks, 'none', multiply_files)
    print(f'Create {format_type} tasks result:', r.content)

    assert r.status_code == status_code, f'Upload one task {format_type} failed. Response data: {r.data}'
    assert Task.objects.filter(project=setup_project_dialog.project.id).count() == task_count * multiplier


@pytest.mark.django_db
def test_yolov8_zip_dataset_upload(setup_project_dialog):
    setup_project_dialog.project.label_config = (
        '<View>'
        '<Image name="image" value="$image"/>'
        '<RectangleLabels name="label" toName="image">'
        '<Label value="cat"/>'
        '<Label value="dog"/>'
        '</RectangleLabels>'
        '</View>'
    )
    setup_project_dialog.project.save(update_fields=['label_config'])

    image_buffer = io.BytesIO()
    Image.new('RGB', (100, 200), color='white').save(image_buffer, format='JPEG')
    image_buffer.seek(0)

    archive_buffer = io.BytesIO()
    with zipfile.ZipFile(archive_buffer, mode='w', compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            'dataset/data.yaml',
            'train: images/train\nval: images/val\nnames:\n  0: cat\n  1: dog\n',
        )
        archive.writestr('dataset/images/train/sample.jpg', image_buffer.getvalue())
        archive.writestr('dataset/labels/train/sample.txt', '0 0.5 0.5 0.4 0.2\n1 0.25 0.25 0.1 0.1\n')
    archive_buffer.seek(0)
    archive_buffer.name = 'dataset.zip'

    response = setup_project_dialog.post(setup_project_dialog.urls.task_bulk, {'dataset.zip': archive_buffer})

    assert response.status_code == 201, response.content

    task = Task.objects.get(project=setup_project_dialog.project.id)
    annotation = Annotation.objects.get(task=task)
    extracted_image_upload = FileUpload.objects.filter(project=setup_project_dialog.project.id, file__endswith='sample.jpg')

    assert 'image' in task.data
    assert task.data['image'].startswith('/data/upload/')
    assert task.data['image'].endswith('.jpg')
    assert extracted_image_upload.count() == 1

    image_response = setup_project_dialog.get(task.data['image'])

    assert image_response.status_code == 200
    assert annotation.ground_truth is True
    assert len(annotation.result) == 2

    first_result = annotation.result[0]
    second_result = annotation.result[1]

    assert first_result['from_name'] == 'label'
    assert first_result['to_name'] == 'image'
    assert first_result['type'] == 'rectanglelabels'
    assert first_result['value']['rectanglelabels'] == ['cat']
    assert first_result['value']['x'] == pytest.approx(30)
    assert first_result['value']['y'] == pytest.approx(40)
    assert first_result['value']['width'] == pytest.approx(40)
    assert first_result['value']['height'] == pytest.approx(20)
    assert first_result['original_width'] == 100
    assert first_result['original_height'] == 200

    assert second_result['value']['rectanglelabels'] == ['dog']
    assert second_result['value']['x'] == pytest.approx(20)
    assert second_result['value']['y'] == pytest.approx(20)
    assert second_result['value']['width'] == pytest.approx(10)
    assert second_result['value']['height'] == pytest.approx(10)


@pytest.mark.django_db
def test_yolov8_zip_reimport_works_when_files_as_tasks_list_is_false(setup_project_dialog):
    setup_project_dialog.project.label_config = (
        '<View>'
        '<Image name="image" value="$image"/>'
        '<RectangleLabels name="label" toName="image">'
        '<Label value="cat"/>'
        '<Label value="dog"/>'
        '</RectangleLabels>'
        '</View>'
    )
    setup_project_dialog.project.save(update_fields=['label_config'])

    image_buffer = io.BytesIO()
    Image.new('RGB', (100, 200), color='white').save(image_buffer, format='JPEG')
    image_buffer.seek(0)

    archive_buffer = io.BytesIO()
    with zipfile.ZipFile(archive_buffer, mode='w', compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            'dataset/data.yaml',
            'train: images/train\nval: images/val\nnames:\n  0: cat\n  1: dog\n',
        )
        archive.writestr('dataset/images/train/sample.jpg', image_buffer.getvalue())
        archive.writestr('dataset/labels/train/sample.txt', '0 0.5 0.5 0.4 0.2\n1 0.25 0.25 0.1 0.1\n')
    archive_bytes = archive_buffer.getvalue()

    file_upload = FileUpload.objects.create(
        user=setup_project_dialog.user,
        project=setup_project_dialog.project,
        file=SimpleUploadedFile('dataset.zip', archive_bytes, content_type='application/zip'),
    )

    response = setup_project_dialog.post(
        f'/api/projects/{setup_project_dialog.project.id}/reimport',
        data=json.dumps({'file_upload_ids': [file_upload.id], 'files_as_tasks_list': False}),
        content_type='application/json',
    )

    assert response.status_code == 201, response.content
    assert response.data['task_count'] == 1
    assert response.data['annotation_count'] == 1

    task = Task.objects.get(project=setup_project_dialog.project.id)
    annotation = Annotation.objects.get(task=task)

    assert 'image' in task.data
    assert task.data['image'].endswith('.jpg')
    assert len(annotation.result) == 2
    assert annotation.result[0]['value']['rectanglelabels'] == ['cat']
    assert annotation.result[1]['value']['rectanglelabels'] == ['dog']


@pytest.mark.django_db
def test_yolov8_zip_upload_auto_adds_missing_rectanglelabels(setup_project_dialog):
    setup_project_dialog.project.label_config = (
        '<View>'
        '<Image name="image" value="$image"/>'
        '<RectangleLabels name="label" toName="image">'
        '<Label value="Airplane"/>'
        '<Label value="Car"/>'
        '</RectangleLabels>'
        '</View>'
    )
    setup_project_dialog.project.save(update_fields=['label_config'])

    image_buffer = io.BytesIO()
    Image.new('RGB', (100, 200), color='white').save(image_buffer, format='JPEG')
    image_buffer.seek(0)

    archive_buffer = io.BytesIO()
    with zipfile.ZipFile(archive_buffer, mode='w', compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            'dataset/data.yaml',
            'train: images/train\nval: images/val\nnames:\n  0: cat\n  1: dog\n',
        )
        archive.writestr('dataset/images/train/sample.jpg', image_buffer.getvalue())
        archive.writestr('dataset/labels/train/sample.txt', '0 0.5 0.5 0.4 0.2\n1 0.25 0.25 0.1 0.1\n')
    archive_buffer.seek(0)
    archive_buffer.name = 'dataset.zip'

    response = setup_project_dialog.post(setup_project_dialog.urls.task_bulk, {'dataset.zip': archive_buffer})

    assert response.status_code == 201, response.content

    setup_project_dialog.project.refresh_from_db()
    assert 'value="cat"' in setup_project_dialog.project.label_config
    assert 'value="dog"' in setup_project_dialog.project.label_config

    annotation = Annotation.objects.get(task__project=setup_project_dialog.project.id)
    assert annotation.result[0]['value']['rectanglelabels'] == ['cat']
    assert annotation.result[1]['value']['rectanglelabels'] == ['dog']


@pytest.mark.parametrize(
    'tasks, status_code, task_count, max_duration',
    [([{'data': {'dialog': 'Test'}, 'annotations': [{'result': [{'id': '123'}]}]}] * 1000, 201, 1000, 30)],
)
@pytest.mark.django_db
def test_upload_duration(setup_project_dialog, tasks, status_code, task_count, max_duration):
    """Upload JSON task with annotation to project"""
    r = post_data_as_format(setup_project_dialog, 'json_data', json.dumps(tasks), 'none', 1)
    print('Create json tasks with annotations result:', r.content)
    assert r.status_code == status_code, ('Upload one task with annotation failed', r.content)

    # tasks
    tasks = Task.objects.filter(project=setup_project_dialog.project.id)
    assert tasks.count() == task_count
    for task in tasks:
        assert task.is_labeled, 'Task should be labeled'

    # check max duration
    result = json.loads(r.content)
    assert result['duration'] < max_duration, 'Max duration of adding tasks is exceeded'


@pytest.mark.parametrize(
    'tasks, status_code, task_count',
    [([{'data': {'dialog': 'Test'}, 'annotations': [{'result': [{'id': '123'}]}]}] * 100, 201, 100)],
)
@pytest.mark.django_db
def test_url_upload(mocker, setup_project_dialog, tasks, status_code, task_count):
    """Upload tasks from URL"""
    with requests_mock.Mocker(real_http=True) as m:
        url = 'http://localhost:8111/test.json'
        m.get(url, text=json.dumps(tasks), headers={'Content-Length': '100'})
        r = setup_project_dialog.post(
            setup_project_dialog.urls.task_bulk, data='url=' + url, content_type='application/x-www-form-urlencoded'
        )
        assert r.status_code == status_code, 'Upload URL failed: ' + str(r.content)

        # tasks
        tasks = Task.objects.filter(project=setup_project_dialog.project.id)
        assert tasks.count() == task_count
        for task in tasks:
            assert task.is_labeled, 'Task should be labeled since annotation is ground_truth'


@pytest.mark.parametrize(
    'tasks, status_code, task_count, bad_token',
    [([{'dialog': 'Test'}] * 1, 201, 1, False), ([{'dialog': 'Test'}] * 1, 401, 0, True)],
)
@pytest.mark.django_db
def test_upload_with_token(setup_project_for_token, tasks, status_code, task_count, bad_token):
    """Upload with Django Token"""
    setup = setup_project_for_token
    token = Token.objects.get(user=setup.user)
    token = 'Token ' + str(token)
    broken_token = 'Token broken'
    data = setup.project_config
    data['organization_pk'] = setup.org.pk
    r = setup.post(setup.urls.project_create, data=data, HTTP_AUTHORIZATION=token)
    print('Project create with status code:', r.status_code, r.content)
    assert r.status_code == 201, 'Create project result should be redirect to the next page: ' + str(r.content)

    project = Project.objects.filter(title=setup.project_config['title']).first()
    setup.urls.set_project(project.pk)

    r = setup.post(
        setup.urls.task_bulk,
        data=json.dumps(tasks),
        content_type='application/json',
        HTTP_AUTHORIZATION=broken_token if bad_token else token,
    )
    assert r.status_code == status_code, 'Create json tasks result: ' + str(r.content)

    # tasks
    tasks = Task.objects.filter(project=project.id)
    assert tasks.count() == task_count
