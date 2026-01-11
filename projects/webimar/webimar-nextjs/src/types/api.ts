export interface StructureType {
  id: number;
  name: string;
  url_key: string;
}

export interface StructureCategory {
  name: string;
  icon: string;
  description: string;
  structures: StructureType[];
}

export interface StructureCategoriesResponse {
  success: boolean;
  data: Record<string, StructureCategory>;
  message: string;
}

export interface SEOMetaData {
  title: string;
  description: string;
  keywords: string;
  og_title: string;
  og_description: string;
  og_image: string;
  canonical_url: string;
  schema_data: {
    '@context': string;
    '@type': string;
    name: string;
    description: string;
    url: string;
    applicationCategory: string;
    operatingSystem: string;
    offers: {
      '@type': string;
      price: string;
      priceCurrency: string;
    };
  };
}

export interface SEOMetaResponse {
  success: boolean;
  data: SEOMetaData;
  message: string;
}
