// Types for the HomePage
export interface YapiTuru {
  id: number;
  ad: string;
}

export interface StructureType {
  id: number;
  name: string;
  url: string;
}

export interface StructureCategory {
  name: string;
  icon: string;
  types: StructureType[];
}

export interface SEOData {
  title?: string;
  description?: string;
  keywords?: string;
}

export interface APIResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}
