import React from 'react';
import LodgementList from './LodgementList';
import { useQuery } from "@tanstack/react-query";
import lodgementService from "../services/lodgementService";
import TagFilter from './TagFilter';
import { useState } from 'react';

const ListLodgementsPage = () => {

    const { data,status,error } = useQuery(["lodgementList",], lodgementService.getLodgementList);
    const [selectedTags, setSelectedTags] = useState([]);

    if (status == "loading") {
        return <div>Loading...</div>;
    }
    if (status == "error") {
        return <div>Error: {error.message}</div>;
    }

    const toggleTag = (tag) => {
        setSelectedTags(prevTags => 
            prevTags.includes(tag) ? prevTags.filter(t => t !== tag) : [...prevTags, tag]
        );
    };
    console.log(selectedTags);

    const tags = new Set();

    data.forEach(element => {
        element.tags.forEach(tag => {
            tags.add(tag);
        })});
    console.log(tags);


    const results=  data.filter(lodgement => {
        if (selectedTags.length === 0) {
            return true;
        }
        return selectedTags.some(tag => lodgement.tags.includes(tag));
    });

    return (
        <div>
            <TagFilter tags={Array.from(tags)} selectedTags={selectedTags} onToggleTag={toggleTag} />
            <LodgementList lodgements={results} />
        </div>
    );
}


export default ListLodgementsPage;