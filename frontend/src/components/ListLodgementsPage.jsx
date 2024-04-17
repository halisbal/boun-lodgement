import React from 'react';
import LodgementList from './LodgementList';
import { useQuery } from "@tanstack/react-query";
import lodgementService from "../services/lodgementService";
const ListLodgementsPage = () => {

    const { data,status,error } = useQuery(["lodgementList",], lodgementService.getLodgementList);

    if (status == "loading") {
        return <div>Loading...</div>;
    }
    if (status == "error") {
        return <div>Error: {error.message}</div>;
    }


    return (
        <div>
            <LodgementList lodgements={data} />
        </div>
    );
}


export default ListLodgementsPage;