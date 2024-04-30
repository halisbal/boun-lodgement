const LodgementCard = ({ lodgement }) => {
    return (
      <div className="max-w-sm rounded overflow-hidden shadow-lg">
        <img className="w-full" src={"/static/"+lodgement.image_path} alt={`${lodgement.title}`} />
        <div className="px-6 py-4">
          <div className="font-bold text-xl mb-2">{lodgement.name}</div>
          <p className="text-gray-700 text-base">
            {lodgement.description}
          </p>
        </div>
        <div className="px-6 pt-4 pb-2">
          {lodgement.tags.map((tag) => (
            <span key={tag} className="inline-block bg-gray-200 rounded-full px-3 py-1 text-sm font-semibold text-gray-700 mr-2 mb-2">
              #{tag}
            </span>
          ))}
        </div>
        <div className="px-6 py-4 flex items-center">
          <span className={`inline-block ${lodgement.is_available ? 'bg-green-200' : 'bg-red-200'} rounded-full px-3 py-1 text-sm font-semibold text-gray-700 mr-2 mb-2`}>
            {lodgement.is_available ? 'Available' : 'Not Available'}
          </span>
        </div>
      </div>
    );
  };

  export default LodgementCard;
  