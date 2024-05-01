import { Select, Option, Button } from "@material-tailwind/react";
import DefaultTable from "./DefaultTable";
import fetchQueues from "../fetchs/fetchQueues";
import { useQuery } from "@tanstack/react-query";
import { apiService } from "../services/apiService";
import { useState } from "react";

const ApplyPage = () => {

    const { data, status, error } = useQuery(["QueueList"], fetchQueues);
    const [selectedQueue, setSelectedQueue] = useState("react");

    if (status === "loading") {
        return <div>Loading...</div>;
    }
    if (status === "error") {
        return <div>Error: {error.message}</div>;
    }

    const applyQueue = () => {
        apiService.post(`/queue/${selectedQueue}/apply/`);
        console.log(selectedQueue);
    }


    return (<div className="container flex justify-center mx-auto h-max items-center min-h-screen">
        <div className="p-5 shadow-md w-6/12 items-center flex justify-center flex-col">
            <div className="flex align-items-center items-center w-11/12 ">
                <label>Başvuracağınız kategoriyi seçiniz</label>
                <Select label="Select Version" id="queueSelect" value={selectedQueue} onChange={(val)=>setSelectedQueue(val)}>
                    {data.map((lodgement) => (
                        <Option key={lodgement.id} value={lodgement.id}>
                            {lodgement.lodgement_type} - {lodgement.personel_type} - {lodgement.lodgement_size}
                        </Option>
                    ))}
                </Select>
            </div>

            <Button variant="outlined" className="w-11/12 py-4 mt-5 text-base " onClick={applyQueue}> Apply</Button>
        </div>
    </div>);
}

export default ApplyPage;