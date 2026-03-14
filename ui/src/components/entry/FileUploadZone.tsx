import { useState, useCallback, useRef } from 'react';
import { 
  Upload, X, FileText, Image, Video, FileSpreadsheet, 
  FileJson, File, CheckCircle
} from 'lucide-react';
import type { UploadedFile } from '../types';
import { getFileType, formatFileSize, generateId, createFilePreview, cn } from '../utils';

interface FileUploadZoneProps {
  files: UploadedFile[];
  onFilesChange: (files: UploadedFile[]) => void;
  maxFiles?: number;
}

const FILE_TYPE_ICONS = {
  image: Image,
  video: Video,
  pdf: FileText,
  csv: FileSpreadsheet,
  json: FileJson,
  unknown: File,
};

const FILE_TYPE_COLORS = {
  image: 'text-purple-400 bg-purple-400/10',
  video: 'text-red-400 bg-red-400/10',
  pdf: 'text-red-500 bg-red-500/10',
  csv: 'text-green-400 bg-green-400/10',
  json: 'text-yellow-400 bg-yellow-400/10',
  unknown: 'text-gray-400 bg-gray-400/10',
};

export function FileUploadZone({ files, onFilesChange, maxFiles = 10 }: FileUploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const processFiles = async (fileList: FileList | null) => {
    if (!fileList) return;
    
    const newFiles: UploadedFile[] = [];
    const remainingSlots = maxFiles - files.length;
    
    for (let i = 0; i < Math.min(fileList.length, remainingSlots); i++) {
      const file = fileList[i];
      const preview = await createFilePreview(file);
      
      const uploadedFile: UploadedFile = {
        id: generateId(),
        file,
        name: file.name,
        size: file.size,
        type: file.type,
        progress: 0,
        preview,
        status: 'uploading',
      };
      
      newFiles.push(uploadedFile);
      
      // Simulate upload progress
      setTimeout(() => {
        const currentFiles = [...files, ...newFiles];
        const updatedFiles = currentFiles.map(f => 
          f.id === uploadedFile.id ? { ...f, progress: 100, status: 'completed' as const } : f
        );
        onFilesChange(updatedFiles);
      }, 500 + Math.random() * 1000);
    }
    
    onFilesChange([...files, ...newFiles]);
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    processFiles(e.dataTransfer.files);
  }, [files]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    processFiles(e.target.files);
    e.target.value = ''; // Reset input
  };

  const removeFile = (id: string) => {
    onFilesChange(files.filter(f => f.id !== id));
  };

  return (
    <div className="space-y-4">
      {/* Upload Zone */}
      <div
        onClick={() => inputRef.current?.click()}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={cn(
          "relative p-8 border-2 border-dashed rounded-2xl cursor-pointer transition-all duration-300",
          "bg-dark-800/30 hover:bg-dark-800/50",
          isDragging 
            ? "border-accent-blue bg-accent-blue/10 scale-[1.02]" 
            : "border-dark-600 hover:border-dark-500"
        )}
      >
        <input
          ref={inputRef}
          type="file"
          multiple
          accept="image/*,video/*,.pdf,.csv,.json,application/pdf,text/csv,application/json"
          onChange={handleInputChange}
          className="hidden"
        />
        
        <div className="flex flex-col items-center text-center space-y-3">
          <div className={cn(
            "p-4 rounded-full transition-all duration-300",
            isDragging ? "bg-accent-blue/20 scale-110" : "bg-dark-700/50"
          )}>
            <Upload className={cn(
              "w-8 h-8 transition-colors",
              isDragging ? "text-accent-blue" : "text-gray-400"
            )} />
          </div>
          
          <div>
            <p className="text-lg font-medium text-white">
              {isDragging ? 'Drop files here' : 'Drag & drop files'}
            </p>
            <p className="text-sm text-gray-400 mt-1">
              or click to browse
            </p>
          </div>
          
          <div className="flex flex-wrap justify-center gap-2 mt-2">
            {['Images', 'Videos', 'PDFs', 'CSV', 'JSON'].map((type) => (
              <span 
                key={type}
                className="px-2 py-1 text-xs bg-dark-700/50 text-gray-400 rounded-md"
              >
                {type}
              </span>
            ))}
          </div>
          
          <p className="text-xs text-gray-500">
            Max {maxFiles} files • Up to 50MB each
          </p>
        </div>
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="space-y-2 animate-fade-in">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-400">
              {files.length} file{files.length !== 1 ? 's' : ''} selected
            </span>
            <button
              onClick={() => onFilesChange([])}
              className="text-xs text-red-400 hover:text-red-300 transition-colors"
            >
              Clear all
            </button>
          </div>
          
          <div className="grid gap-2 max-h-64 overflow-y-auto pr-1">
            {files.map((file, index) => {
              const fileType = getFileType(file.file);
              const Icon = FILE_TYPE_ICONS[fileType];
              const colorClass = FILE_TYPE_COLORS[fileType];
              
              return (
                <div
                  key={file.id}
                  className="group flex items-center gap-3 p-3 bg-dark-800/50 rounded-xl border border-dark-600/50 
                           hover:border-dark-500 transition-all duration-200 animate-slide-up"
                  style={{ animationDelay: `${index * 50}ms` }}
                >
                  {/* Preview or Icon */}
                  <div className="relative w-12 h-12 flex-shrink-0">
                    {file.preview && fileType === 'image' ? (
                      <img 
                        src={file.preview} 
                        alt={file.name}
                        className="w-full h-full object-cover rounded-lg"
                      />
                    ) : (
                      <div className={cn("w-full h-full rounded-lg flex items-center justify-center", colorClass)}>
                        <Icon className="w-6 h-6" />
                      </div>
                    )}
                    
                    {/* Status indicator */}
                    {file.status === 'completed' && (
                      <div className="absolute -bottom-1 -right-1 w-5 h-5 bg-green-500 rounded-full 
                                    flex items-center justify-center">
                        <CheckCircle className="w-3 h-3 text-white" />
                      </div>
                    )}
                  </div>
                  
                  {/* File info */}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-white truncate">
                      {file.name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {formatFileSize(file.size)}
                    </p>
                    
                    {/* Progress bar */}
                    {file.status === 'uploading' && (
                      <div className="mt-1.5">
                        <div className="h-1 bg-dark-700 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-gradient-to-r from-accent-blue to-accent-cyan rounded-full 
                                     transition-all duration-300"
                            style={{ width: `${file.progress}%` }}
                          />
                        </div>
                      </div>
                    )}
                  </div>
                  
                  {/* Remove button */}
                  <button
                    onClick={() => removeFile(file.id)}
                    className="p-2 text-gray-500 hover:text-red-400 hover:bg-red-400/10 
                             rounded-lg transition-all duration-200 opacity-0 group-hover:opacity-100"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}