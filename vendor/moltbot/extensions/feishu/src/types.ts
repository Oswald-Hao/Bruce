// Feishu/Lark API Types

export type FeishuUser = {
  user_id?: string;
  name?: string;
  en_name?: string;
  email?: string;
  avatar_url?: string;
};

export type FeishuChatType = "private" | "group" | "p2p";

export type FeishuEvent = {
  // Base event fields
  schema?: string;
  header?: {
    event_id?: string;
    event_type?: string;
    create_time?: string;
    token?: string;
    app_id?: string;
    tenant_key?: string;
  };
  // Event-specific data
  event?: {
    // Message received event
    sender?: FeishuUser;
    message?: {
      message_id?: string;
      chat_type?: FeishuChatType;
      chat_id?: string;
      content?: string;
      create_time?: string;
      updated?: string;
      msg_type?: string;
      parent_id?: string;
      root_id?: string;
    };
    // Other event types...
  };
};

export type FeishuMessageContent = {
  text?: string;
  post?: FeishuPostContent;
  image?: { image_key: string };
  file?: { file_key: string };
  audio?: { file_key: string };
  video?: { file_key: string };
  media?: { file_key: string };
  sticker?: { file_key: string };
  [key: string]: unknown;
};

export type FeishuPostContent = {
  zh_cn?: FeishuPostElement[];
  en_us?: FeishuPostElement[];
};

export type FeishuPostElement = {
  tag: string;
  text?: string;
  href?: string;
  user_id?: string;
  [key: string]: unknown;
};

export type FeishuSendMessageRequest = {
  receive_id_type?: "open_id" | "user_id" | "union_id" | "chat_id";
  receive_id?: string;
  msg_type?: "text" | "post" | "image" | "file" | "audio" | "video" | "media" | "sticker" | "interactive";
  content?: string | Record<string, unknown>;
  uuid?: string;
};

export type FeishuSendMessageResponse = {
  code?: number;
  msg?: string;
  data?: {
    msg_id?: string;
    [key: string]: unknown;
  };
};

export type FeishuUserInfo = {
  user_id?: string;
  name?: string;
  en_name?: string;
  email?: string;
  mobile?: string;
  avatar_url?: string;
  status?: Record<string, unknown>;
};

export type FeishuChatInfo = {
  name?: string;
  description?: string;
  avatar?: string;
  owner_id?: string;
  chat_mode?: string;
  chat_type?: FeishuChatType;
  external?: boolean;
  tenant_key?: string;
};

export type FeishuAttachment = {
  file_key?: string;
  file_type?: string;
  name?: string;
  url?: string;
  size?: number;
};

export type FeishuMediaUploadResponse = {
  code?: number;
  msg?: string;
  data?: {
    file_key?: string;
    [key: string]: unknown;
  };
};
