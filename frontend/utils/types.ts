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

export interface Collection {
  uuid: string,
  id: string,
  title: string,
  description: string,
  license_title: string,
  bbox: Array<number>,
  bbox_crs: string,
  interval: string,
  crs: Array<string>,
  storage_crs: string,
  storage_crs_coordinate_epoch: number,

  connection_name: string,
  url: string,
}

export interface Namespace {
  uuid: string,
  name: string,
  url: string
}

export interface GeneralOption {
  key: string,
  value: string
}