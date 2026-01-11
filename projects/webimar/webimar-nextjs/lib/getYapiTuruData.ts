import fs from 'fs';
import path from 'path';
import { YapiTuruData } from '../data/schema/yapi-turu-schema';

/**
 * Tüm yapı türlerinin slug listesini döndürür
 */
export async function getAllYapiTuruSlugs(): Promise<string[]> {
  const dataDirectory = path.join(process.cwd(), 'data', 'yapi-turleri');
  
  try {
    const fileNames = fs.readdirSync(dataDirectory);
    return fileNames
      .filter(fileName => fileName.endsWith('.json'))
      .map(fileName => fileName.replace(/\.json$/, ''));
  } catch (error) {
    console.error('Yapı türleri okunamadı:', error);
    return [];
  }
}

/**
 * Belirli bir yapı türünün verilerini döndürür
 */
export async function getYapiTuruData(slug: string): Promise<YapiTuruData | null> {
  const dataDirectory = path.join(process.cwd(), 'data', 'yapi-turleri');
  const filePath = path.join(dataDirectory, `${slug}.json`);

  try {
    const fileContents = fs.readFileSync(filePath, 'utf8');
    const data: YapiTuruData = JSON.parse(fileContents);
    return data;
  } catch (error) {
    console.error(`${slug} verisi okunamadı:`, error);
    return null;
  }
}

/**
 * Tüm yapı türlerinin özet bilgilerini döndürür
 */
export async function getAllYapiTurleri() {
  const slugs = await getAllYapiTuruSlugs();
  const yapiTurleri = await Promise.all(
    slugs.map(async (slug) => {
      const data = await getYapiTuruData(slug);
      if (!data) return null;
      
      return {
        slug: data.slug,
        name: data.name,
        category: data.category,
        icon: data.hero.icon,
        description: data.seo.description,
      };
    })
  );

  return yapiTurleri.filter((item) => item !== null);
}

/**
 * Kategoriye göre yapı türlerini gruplar
 */
export async function getYapiTurleriByCategory() {
  const allYapiTurleri = await getAllYapiTurleri();
  
  const categories: Record<string, any[]> = {};
  
  allYapiTurleri.forEach((yapi) => {
    if (!yapi) return;
    
    if (!categories[yapi.category]) {
      categories[yapi.category] = [];
    }
    categories[yapi.category].push(yapi);
  });

  return categories;
}
