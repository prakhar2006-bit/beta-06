import { supabase } from '../lib/supabaseClient';

const extensionFor = (file) => file.type === 'application/pdf' ? 'pdf' : file.type.split('/')[1] === 'jpeg' ? 'jpg' : file.type.split('/')[1];

const prepareImage = (file) => new Promise((resolve, reject) => {
  if (!file.type.startsWith('image/')) return resolve(file);
  const image = new Image(); const url = URL.createObjectURL(file);
  image.onload = () => {
    const scale = Math.min(1, 1600 / Math.max(image.width, image.height));
    const canvas = document.createElement('canvas'); canvas.width = Math.round(image.width * scale); canvas.height = Math.round(image.height * scale);
    canvas.getContext('2d').drawImage(image, 0, 0, canvas.width, canvas.height);
    canvas.toBlob((blob) => { URL.revokeObjectURL(url); blob ? resolve(new File([blob], file.name.replace(/\.[^.]+$/, '.jpg'), { type: 'image/jpeg' })) : reject(new Error('IMAGE_PREPARE_FAILED')); }, 'image/jpeg', 0.86);
  }; image.onerror = () => { URL.revokeObjectURL(url); reject(new Error('IMAGE_PREPARE_FAILED')); }; image.src = url;
});

export const uploadDocument = async (userId, type, file) => {
  if (!supabase) throw new Error('AUTH_UNAVAILABLE');
  if (file.size > 3 * 1024 * 1024 || !['image/jpeg', 'image/png', 'application/pdf'].includes(file.type)) throw new Error('DOCUMENT_NOT_ALLOWED');
  const prepared = await prepareImage(file); const path = `${userId}/${type}/${crypto.randomUUID()}.${extensionFor(prepared)}`;
  const upload = await supabase.storage.from('user-documents').upload(path, prepared, { contentType: prepared.type, upsert: false });
  if (upload.error) throw upload.error;
  const result = await supabase.from('user_documents').insert({ user_id: userId, doc_type: type, storage_path: path, file_name: prepared.name, size_bytes: prepared.size, mime_type: prepared.type, expires_at: new Date(Date.now() + 90 * 86400000).toISOString() }).select().single();
  if (result.error) { await supabase.storage.from('user-documents').remove([path]); throw result.error; }
  return result.data;
};

export const signedDocumentUrl = async (path) => {
  const result = await supabase.storage.from('user-documents').createSignedUrl(path, 60);
  if (result.error) throw result.error; return result.data.signedUrl;
};
