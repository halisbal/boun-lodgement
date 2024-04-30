import React from 'react';

const TagFilter = ({ tags, selectedTags, onToggleTag }) => {

    console.log(tags);
  return (
    <div className="flex justify-center gap-2 py-5">
      {tags.map(tag => (
        <div>
        <button
          key={tag}
          onClick={() => onToggleTag(tag)}
          className={`px-4 py-2 border rounded-full cursor-pointer text-sm font-medium ${
            selectedTags.includes(tag) ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800'
          }`}
        >
          {selectedTags.includes(tag) ? `✓ ${tag}` : tag}
        </button>
        </div>
      ))}
    </div>
  );
};

export default TagFilter;