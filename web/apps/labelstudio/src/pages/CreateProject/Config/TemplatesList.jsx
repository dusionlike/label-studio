import React from "react";
import { Spinner } from "../../../components";
import { useAPI } from "../../../providers/ApiProvider";
import { cn } from "../../../utils/bem";
import "./Config.prefix.css";
import { IconInfo } from "@humansignal/icons";
import { Button, EnterpriseBadge } from "@humansignal/ui";

const listClass = cn("templates-list");

const GROUP_TRANSLATIONS = {
  "Computer Vision": "计算机视觉",
  "Natural Language Processing": "自然语言处理",
  "Audio/Speech Processing": "音频/语音处理",
  "Conversational AI": "对话式 AI",
  Chat: "对话",
  "Ranking & Scoring": "排序与评分",
  "Structured Data Parsing": "结构化数据解析",
  "Time Series Analysis": "时序分析",
  Videos: "视频",
  "Generative AI": "生成式 AI",
  "Community Contributions": "社区贡献",
};

const TEMPLATE_TITLE_TRANSLATIONS = {
  "Object Detection with Bounding Boxes": "目标检测（边界框）",
  "Image Classification": "图像分类",
  "Named Entity Recognition": "命名实体识别",
  "Text Classification": "文本分类",
  "Relation Extraction": "关系抽取",
  "Question Answering": "问答标注",
  Taxonomy: "分类体系标注",
  "Optical Character Recognition": "光学字符识别",
  Keypoints: "关键点标注",
  "Semantic Segmentation with Polygons": "多边形语义分割",
  "Semantic Segmentation with Masks": "掩码语义分割",
  "Visual Question Answering": "视觉问答",
  "Speech Transcription": "语音转写",
  "Intent Classification": "意图分类",
  "Video Classification": "视频分类",
  "Video Object Tracking": "视频目标跟踪",
  "Video Frame Classification": "视频帧分类",
  "Video Timeline Segmentation": "视频时间轴分段",
  "Tabular Data": "表格数据标注",
  "Freeform Metadata": "自由元数据标注",
  "Content Moderation": "内容审核",
  "OCR Labeling for PDFs": "PDF OCR 标注",
  "Keypoint Labeling": "关键点标注",
  "Inventory Tracking": "库存跟踪标注",
  "Image Captioning": "图像描述标注",
  "Visual Genome": "视觉基因组标注",
  "Medical Image Classification with Bounding Boxes": "医学图像分类（边界框）",
  "Multi-page document annotation": "多页文档标注",
  "Automatic Speech Recognition": "自动语音识别",
  "Automatic Speech Recognition Using Segments": "分段自动语音识别",
  "Conversational Analysis": "对话分析",
  "Sound Event Detection": "声音事件检测",
  "Signal Quality Detection": "信号质量检测",
  "Speaker Segmentation": "说话人分割",
  "Question Answering with Context": "上下文问答标注",
  "Machine Translation": "机器翻译标注",
  "Text Summarization": "文本摘要标注",
  "Coreference Resolution and Entity Linking": "指代消解与实体链接",
  "Intent Classification and Slot Filling": "意图分类与槽位填充",
  "Response Selection": "回复选择",
  "Response Generation": "回复生成",
  "Document Retrieval": "文档检索排序",
  "Text to Image": "文生图排序",
  "Pairwise Regression": "成对回归评估",
  "Pairwise Classification": "成对分类评估",
  "SERP Ranking": "搜索结果排序",
  "ASR Hypotheses": "ASR 候选结果排序",
  "Content-based Image Search": "基于内容的图像检索",
  "Outliers & Anomaly Detection": "离群点与异常检测",
  "Activity Recognition": "活动识别",
  "Change Point Detection": "变点检测",
  "Signal Quality": "信号质量标注",
  "Time Series Forecasting": "时序预测标注",
  "Human Feedback Collection": "人工反馈采集",
  "Response Grading": "回复评分",
  "Supervised LLM": "监督式 LLM 标注",
  "Visual Ranker": "视觉排序器",
  "LLM Ranker": "LLM 排序器",
  "Chatbot Assessment": "聊天机器人评估",
  Chatbot: "聊天机器人",
};

const translateGroup = (group) => GROUP_TRANSLATIONS[group] ?? group;
const translateTitle = (title) => TEMPLATE_TITLE_TRANSLATIONS[title] ?? title;

const Arrow = () => (
  <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">
    <title>箭头图标</title>
    <path opacity="0.9" d="M2 10L6 6L2 2" stroke="currentColor" strokeWidth="2" strokeLinecap="square" />
  </svg>
);

const TemplatesInGroup = ({ templates, group, onSelectRecipe, isEdition }) => {
  const picked = templates
    .filter((recipe) => recipe.group === group)
    // templates without `order` go to the end of the list
    .sort((a, b) => (a.order ?? Number.POSITIVE_INFINITY) - (b.order ?? Number.POSITIVE_INFINITY));

  const isCommunityEdition = isEdition === "Community";

  return (
    <ul>
      {picked.map((recipe) => {
        const isEnterpriseTemplate = recipe.type === "enterprise";
        const isDisabled = isCommunityEdition && isEnterpriseTemplate;

        return (
          <li
            key={recipe.title}
            onClick={() => !isDisabled && onSelectRecipe(recipe)}
            className={listClass.elem("template").mod({ disabled: isDisabled }).toClassName()}
            title={isDisabled ? "企业版功能，仅 Label Studio Enterprise 可用" : ""}
          >
            <img src={recipe.image} alt={""} />
            <div className="flex flex-col items-center w-full">
              <h3 className="flex flex-1 justify-center text-center w-full">{translateTitle(recipe.title)}</h3>
              {isEnterpriseTemplate && isCommunityEdition && <EnterpriseBadge className="mb-base" />}
            </div>
          </li>
        );
      })}
    </ul>
  );
};

export const TemplatesList = ({ selectedGroup, selectedRecipe, onCustomTemplate, onSelectGroup, onSelectRecipe }) => {
  const [groups, setGroups] = React.useState([]);
  const [templates, setTemplates] = React.useState();
  const api = useAPI();
  const isEdition = window?.APP_SETTINGS?.version_edition;

  React.useEffect(() => {
    const fetchData = async () => {
      const res = await api.callApi("configTemplates");

      if (!res) return;
      const { templates, groups } = res;

      setTemplates(templates);
      setGroups(groups);
    };
    fetchData();
  }, []);

  const selected = selectedGroup || groups[0];

  return (
    <div className={listClass}>
      <aside className={listClass.elem("sidebar").toClassName()}>
        <ul>
          {groups.map((group) => (
            <li
              key={group}
              onClick={() => onSelectGroup(group)}
              className={listClass
                .elem("group")
                .mod({
                  active: selected === group,
                  selected: selectedRecipe?.group === group,
                })
                .toClassName()}
            >
              {translateGroup(group)}
              <Arrow />
            </li>
          ))}
        </ul>
        <Button
          type="button"
          align="left"
          look="string"
          size="small"
          onClick={onCustomTemplate}
          className="w-full"
          aria-label="创建自定义模板"
        >
          自定义模板
        </Button>
      </aside>
      <main>
        {!templates && <Spinner style={{ width: "100%", height: 200 }} />}
        <TemplatesInGroup
          templates={templates || []}
          group={selected}
          onSelectRecipe={onSelectRecipe}
          isEdition={isEdition}
        />
      </main>
      <footer className="flex items-center justify-center gap-1">
        <IconInfo className={listClass.elem("info-icon").toClassName()} width="20" height="20" />
        <span>
          如需补充模板，请参考文档{" "}
          <a href="https://labelstud.io/guide" target="_blank" rel="noreferrer">
            提交模板
          </a>
          。
        </span>
      </footer>
    </div>
  );
};
