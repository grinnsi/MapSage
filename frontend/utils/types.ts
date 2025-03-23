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
  connection_name: string,
  url: string,
}

export interface CollectionDetail extends Collection {
  license_title: string,
  extent: {
    spatial: {
      bbox: Array<Array<number>>,
      crs: string
    },
    temporal: {
      interval: Array<Array<string>>,
      trs: string
    }
  },
  date_time_fields: Array<string>;
  selected_date_time_field: string;
  crs: Array<string>,
  storage_crs: string,
  storage_crs_coordinate_epoch: number,
}

export interface Namespace {
  uuid: string,
  name: string,
  url: string
}

export interface GeneralOption {
  key: string,
  data: string
}