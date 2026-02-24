/* --- IMAGE PROCESSING UTILITY --- */

export const processCropImage = (
  fullImageUrl: string, 
  crop: any, 
  onComplete: (base64Image: string) => void
) => {
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  const img = new Image();
  
  img.onload = () => {
    const scale = crop.devicePixelRatio || 1; 
    canvas.width = crop.width * scale;
    canvas.height = crop.height * scale;
    
    ctx?.drawImage(
      img, 
      crop.x * scale, crop.y * scale, crop.width * scale, crop.height * scale, 
      0, 0, canvas.width, canvas.height
    );
    
    // Pass the final base64 string back to the React component
    onComplete(canvas.toDataURL('image/jpeg', 0.8));
  };
  
  img.src = fullImageUrl;
};