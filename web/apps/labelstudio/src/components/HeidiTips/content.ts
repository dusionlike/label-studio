import type { TipsCollection } from "./types";

export const defaultTipsCollection: TipsCollection = {
  projectCreation: [
    {
      title: "你知道吗？",
      content: "使用 Label Studio Enterprise 将项目归类到工作区后，查找和管理项目会更方便。",
      closable: true,
      link: {
        label: "了解更多",
        url: "https://docs.humansignal.com/guide/manage_projects#Create-workspaces-to-organize-projects",
        params: {
          experiment: "project_creation_tip",
          treatment: "find_and_manage_projects",
        },
      },
    },
    {
      title: "更快完成权限分配",
      content:
        "在 Label Studio Enterprise 中通过工作区分配成员，可以更高效地为多个项目配置访问权限。",
      closable: true,
      link: {
        label: "了解更多",
        url: "https://docs.humansignal.com/guide/manage_projects#Add-or-remove-members-to-a-workspace",
        params: {
          experiment: "project_creation_tip",
          treatment: "faster_provisioning",
        },
      },
    },
    {
      title: "你知道吗？",
      content:
        "在企业版平台中，管理员可以查看标注员绩效看板，用于优化资源分配、提升团队管理并辅助绩效评估。",
      closable: true,
      link: {
        label: "了解更多",
        url: "https://docs.humansignal.com/guide/dashboard_annotator",
        params: {
          experiment: "project_creation_tip",
          treatment: "annotator_dashboard",
        },
      },
    },
    {
      title: "你知道吗？",
      content:
        "使用 Label Studio Enterprise，可以为内部成员和外部标注员精细控制项目与工作区访问权限。",
      closable: true,
      link: {
        label: "了解更多",
        url: "https://docs.humansignal.com/guide/manage_users#Roles-in-Label-Studio-Enterprise",
        params: {
          experiment: "project_creation_tip",
          treatment: "access_to_projects",
        },
      },
    },
    {
      title: "你知道吗？",
      content:
        "你可以直接使用或修改数十种模板来配置标注界面，也可以通过简单的类 XML 标签从零创建自定义配置。",
      closable: true,
      link: {
        label: "了解更多",
        url: "https://labelstud.io/guide/setup",
        params: {
          experiment: "project_creation_tip",
          treatment: "templates",
        },
      },
    },
    {
      title: "GenAI 标注模板",
      content:
        "Label Studio 提供了适用于 LLM 监督微调、RAG 检索排序、RLHF、聊天机器人评估等场景的模板。",
      closable: true,
      link: {
        label: "查看模板",
        url: "https://labelstud.io/templates/gallery_generative_ai",
        params: {
          experiment: "project_creation_tip",
          treatment: "genai_templates",
        },
      },
    },
  ],
  organizationPage: [
    {
      title: "你的团队正在扩大！",
      content:
        "通过 Label Studio Enterprise 为团队成员分配角色，并在项目和工作区级别控制敏感数据访问。",
      closable: true,
      link: {
        label: "了解更多",
        url: "https://docs.humansignal.com/guide/manage_users#Roles-in-Label-Studio-Enterprise",
        params: {
          experiment: "organization_page_tip",
          treatment: "team_growing",
        },
      },
    },
    {
      title: "想让登录更简单也更安全？",
      content: "在 Label Studio Enterprise 中，可通过 SAML、SCIM2 或 LDAP 为团队启用单点登录。",
      closable: true,
      link: {
        label: "了解更多",
        url: "https://docs.humansignal.com/guide/auth_setup",
        params: {
          experiment: "organization_page_tip",
          treatment: "enable_sso",
        },
      },
    },
    {
      title: "你知道吗？",
      content: "可以试用面向小团队和小型项目优化的 Label Studio Starter Cloud。",
      closable: true,
      link: {
        label: "了解更多",
        url: "https://humansignal.com/pricing/",
        params: {
          experiment: "organization_page_tip",
          treatment: "starter_cloud_live",
        },
      },
    },
    {
      title: "想自动分发任务吗？",
      content:
        "你可以创建规则，自动将任务分发给标注员，并只向每位标注员展示分配给自己的任务，同时控制任务可见性。",
      closable: true,
      link: {
        label: "了解更多",
        url: "https://docs.humansignal.com/guide/setup_project#Set-up-annotation-settings-for-your-project",
        params: {
          experiment: "organization_page_tip",
          treatment: "automate_distribution",
        },
      },
    },
    {
      title: "与社区分享经验",
      content:
        "如果你有问题，或想和其他 Label Studio 用户交流经验，可以加入社区 Slack 获取最新动态。",
      closable: true,
      link: {
        label: "加入社区",
        url: "https://label-studio.slack.com",
        params: {
          experiment: "organization_page_tip",
          treatment: "share_knowledge",
        },
      },
    },
    {
      title: "你知道吗？",
      content:
        "Label Studio 支持与云存储、机器学习模型及多种常用工具集成，帮助你自动化机器学习流程。",
      closable: true,
      link: {
        label: "查看集成目录",
        url: "https://labelstud.io/integrations/",
        params: {
          experiment: "organization_page_tip",
          treatment: "integration_points",
        },
      },
    },
  ],
  projectSettings: [
    {
      title: "将 AWS 预算用于 Label Studio Enterprise",
      content:
        "Label Studio Enterprise 现已上架 AWS Marketplace，你可以利用已承诺的 AWS 预算优化数据标注流程。",
      closable: true,
      link: {
        label: "了解更多",
        url: "https://aws.amazon.com/marketplace/pp/prodview-wjac3msf77tny",
        params: {
          experiment: "project_settings_tip",
          treatment: "aws_marketplace",
        },
      },
    },
    {
      title: "用自动标注节省时间",
      content:
        "在企业版平台中使用自动化能力，可快速标注大规模数据集，同时兼顾质量。",
      closable: true,
      link: {
        label: "了解更多",
        url: "https://docs.humansignal.com/guide/prompts_overview#Auto-labeling-with-Prompts",
        params: {
          experiment: "project_settings_tip",
          treatment: "auto_labeling",
        },
      },
    },
    {
      title: "你知道吗？",
      content:
        "通过 Label Studio Enterprise 的审核流和任务一致性评分，可以提升标注数据质量。",
      closable: true,
      link: {
        label: "了解更多",
        url: "https://docs.humansignal.com/guide/quality",
        params: {
          experiment: "project_settings_tip",
          treatment: "quality_and_agreement",
        },
      },
    },
    {
      title: "评估 GenAI 模型",
      content:
        "在企业版平台中结合自动化与人工审核，评估并保障 LLM 质量。",
      closable: true,
      link: {
        label: "了解更多",
        url: "https://humansignal.com/evals/",
        params: {
          experiment: "project_settings_tip",
          treatment: "evals",
        },
      },
    },
    {
      title: "你知道吗？",
      content:
        "使用企业云服务可以减少基础设施与升级维护成本，并获得更多自动化、质量控制和团队管理能力。",
      closable: true,
      link: {
        label: "了解更多",
        url: "https://humansignal.com/platform/",
        params: {
          experiment: "project_settings_tip",
          treatment: "infrastructure_and_upgrades",
        },
      },
    },
    {
      title: "你知道吗？",
      content: "可以试用面向小团队和小型项目优化的 Label Studio Starter Cloud。",
      link: {
        label: "了解更多",
        url: "https://humansignal.com/pricing/",
        params: {
          experiment: "project_settings_tip",
          treatment: "starter_cloud_live",
        },
      },
    },
    {
      title: "你知道吗？",
      content: "你可以通过后端 SDK 接入机器学习模型，以便进行预标注或主动学习，节省时间。",
      closable: true,
      link: {
        label: "了解更多",
        url: "https://labelstud.io/guide/ml",
        params: {
          experiment: "project_settings_tip",
          treatment: "connect_ml_models",
        },
      },
    },
  ],
};
