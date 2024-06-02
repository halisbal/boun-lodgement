import React from 'react';

const MyAlert = ({ message, type, onClose, visible }) => {
    const alertColors = {
        success: 'bg-green-100 border-green-500 text-green-700',
        error: 'bg-red-100 border-red-500 text-red-700',
        warning: 'bg-yellow-100 border-yellow-500 text-yellow-700',
        info: 'bg-blue-100 border-blue-500 text-blue-700',
    };

    return (
        <div
            className={`fixed top-4 left-1/2 transform -translate-x-1/2 w-11/12 md:w-1/3 p-4 border-l-4 ${alertColors[type]} rounded-md shadow-md z-50 transition-transform transition-opacity duration-500 ease-out ${visible ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-12 pointer-events-none'}`}

            role="alert"
        >
            <div className="flex items-center justify-between">
                <span>{message}</span>
                <button onClick={onClose} className="ml-2">
                    <svg className="w-5 h-5 text-gray-700" fill="currentColor" viewBox="0 0 20 20">
                        <path
                            fillRule="evenodd"
                            d="M6.293 4.293a1 1 0 011.414 0L10 6.586l2.293-2.293a1 1 0 111.414 1.414L11.414 8l2.293 2.293a1 1 0 01-1.414 1.414L10 9.414l-2.293 2.293a1 1 0 01-1.414-1.414L8.586 8 6.293 5.707a1 1 0 010-1.414z"
                            clipRule="evenodd"
                        />
                    </svg>
                </button>
            </div>
        </div>
    );
};

export default MyAlert;