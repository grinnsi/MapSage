export enum StyleType {
  Normal = "primary",
  Info = "info",
  Success = "success",
  Danger = "danger",
  Warning = "warning"
}

export enum DialogType {
  Form,
  Confirmation,
  Blank
}

export interface Connection {
  uuid: string,
  name: string,
  host: string,
  port: number,
  role: string,
  password: string,
  database_name: string
}

export interface Namespace {
  uuid: string,
  name: string,
  url: string
}