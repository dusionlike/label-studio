/**
 * Constants for the preview components
 */

/** Message shown when large config detected and manual update mode is active */
export const LARGE_CONFIG_MESSAGE = "检测到大型标注界面。为保证性能，预览已关闭自动更新。";

/**
 * Threshold in tag count for switching to manual update mode.
 * MST performance degrades with many nodes - each XML tag becomes an MST node.
 * ~200 tags is where initialization/updates start showing noticeable delays.
 */
export const LARGE_CONFIG_TAG_THRESHOLD = 200;
