export interface Recipe {
  id: number;
  title: string;
  description: string;
  ingredients: string;
  instructions: string;
  author_id: number;
  created_at: string; 
  category?: string;
  imageSource?: string;
}