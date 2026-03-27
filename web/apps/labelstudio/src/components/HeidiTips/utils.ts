import { defaultTipsCollection } from "./content";
import type { Tip, TipsCollection } from "./types";

const STORE_KEY = "heidi_ignored_tips";
const EVENT_NAMESPACE_KEY = "heidi_tips";
const CACHE_KEY = "heidi_live_tips_collection";
const CACHE_FETCHED_AT_KEY = "heidi_live_tips_collection_fetched_at";
const CACHE_STALE_TIME = 1000 * 60 * 60; // 1 hour
const MAX_TIMEOUT = 5000; // 5 seconds

function getKey(collection: string) {
  return `${STORE_KEY}:${collection}`;
}

export function getTipCollectionEvent(collection: string, event: string) {
  return `${EVENT_NAMESPACE_KEY}.${collection}.${event}`;
}

export function getTipEvent(collection: string, tip: Tip, event: string) {
  if (tip.link.params?.experiment && tip.link.params?.treatment) {
    return `${EVENT_NAMESPACE_KEY}.${collection}.${tip.link.params?.experiment}.${tip.link.params?.treatment}.${event}`;
  }
  if (tip.link.params?.experiment) {
    return `${EVENT_NAMESPACE_KEY}.${collection}.${tip.link.params?.experiment}.${event}`;
  }
  if (tip.link.params?.treatment) {
    return `${EVENT_NAMESPACE_KEY}.${collection}.${tip.link.params?.treatment}.${event}`;
  }

  return getTipCollectionEvent(collection, event);
}

export function getTipMetadata(tip: Tip) {
  // Everything except the experiment and treatment params as those are part of the event name
  const { experiment, treatment, ...rest } = tip.link.params ?? {};
  return {
    ...rest,
    content: tip.description ?? tip.content ?? "",
    title: tip.title,
    href: tip.link.url,
    label: tip.link.label,
  };
}

export const loadLiveTipsCollection = () => {
  return defaultTipsCollection;
};

export function getRandomTip(collection: keyof TipsCollection): Tip | null {
  const tipsCollection = loadLiveTipsCollection();

  if (!tipsCollection[collection] || isTipDismissed(collection)) return null;

  const tips = tipsCollection[collection];

  const index = Math.floor(Math.random() * tips.length);

  return tips[index];
}

/**
 * Set a cookie that indicates that a collection of tips is dismissed
 * for 30 days
 */
export function dismissTip(collection: string) {
  // will expire in 30 days
  const cookieExpiryTime = 1000 * 60 * 60 * 24 * 30;
  const cookieExpiryDate = new Date();

  cookieExpiryDate.setTime(cookieExpiryDate.getTime() + cookieExpiryTime);

  const finalKey = getKey(collection);
  const cookieValue = `${finalKey}=true`;
  const cookieExpiry = `expires=${cookieExpiryDate.toUTCString()}`;
  const cookiePath = "path=/";
  const cookieString = [cookieValue, cookieExpiry, cookiePath].join("; ");
  document.cookie = cookieString;

  __lsa(getTipCollectionEvent(collection, "dismiss"), {
    expires: cookieExpiryDate.getTime(),
  });
}

export function isTipDismissed(collection: string) {
  const cookies = Object.fromEntries(document.cookie.split(";").map((item) => item.trim().split("=")));
  const finalKey = getKey(collection);

  return cookies[finalKey] === "true";
}

export function createURL(url: string, params?: Record<string, string>): string {
  const base = new URL(url);

  Object.entries(params ?? {}).forEach(([key, value]) => {
    base.searchParams.set(key, value);
  });

  const userID = APP_SETTINGS.user?.id;
  const serverID = APP_SETTINGS.server_id;

  if (serverID) base.searchParams.set("server_id", serverID);
  if (userID) base.searchParams.set("user_id", userID);

  return base.toString();
}
