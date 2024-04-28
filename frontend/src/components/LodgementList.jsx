import LodgementCard from "./LodgementCard";

const LodgementList = ({lodgements}) => {
    
    return (
        <div className="container mx-auto px-4">
            <h1 className="text-4xl font-bold my-8">Lodgements</h1>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-8">
                {lodgements.map((lodgement) => (
                    <LodgementCard key={lodgement.id} lodgement={lodgement} />
                ))}
            </div>
        </div>
    );
};

export default LodgementList;