import { Select, Option, Button, Accordion, AccordionBody, AccordionHeader, Tooltip } from "@material-tailwind/react";
import fetchQueues from "../fetches/fetchQueues";
import { useQuery } from "@tanstack/react-query";
import { apiService } from "../services/apiService";
import { useState, useEffect } from "react";
import { Input, Checkbox, Card, List, ListItem } from "@material-tailwind/react";
import fetchScoringForm from "../fetches/fetchScoringForm";
import MyAlert from "./MyAlert";
import { useNavigate } from "react-router-dom";

const ApplyPage = () => {

    const scoreFormQuery = useQuery(["scoringForm"], fetchScoringForm);
    const queueQuery = useQuery(["QueueList"], fetchQueues);

    const [selectedQueue, setSelectedQueue] = useState();
    const [evalStats, setEvalStats] = useState({});
    const [formValues, setFormValues] = useState({});
    const [open, setOpen] = useState(0);
    const [alert, setAlert] = useState({ visible: false, message: "", type: "" });


    const navigate = useNavigate();

    const handleOpen = (value) => {
        console.log(selectedQueue)
        if (selectedQueue === undefined) {
            alert("Please select a queue first");
            return;
        }
        setOpen(open === value ? 0 : value)
    };

    useEffect(() => {
        apiService.get("/scoring_form/1/get_latest/").then((response) => {
            response.map((item) => {
                setFormValues(prev => ({ ...prev, [item.scoring_form_item_id]: item.answer }));
            });
        })
    }, []);


    console.log(scoreFormQuery);
    console.log(queueQuery);

    if (queueQuery.status === "loading") {
        return <div>Loading...</div>;
    }
    if (queueQuery.status === "error") {
        return <div>Error: {error.message}</div>;
    }

    const applyQueue = () => {

        if (selectedQueue === undefined) {
            showAlert("Please select a queue first", "error");
            return;
        }

        showAlert("Applying...", "info");
        apiService.post(`/queue/${selectedQueue}/apply/`).then((response) => {
            showAlert("Application completed successfully", "success");
            setTimeout(() => {
                navigate("/my-applications");
            }, 500);
            
        }).catch((error) => {
            showAlert("An error occured while applying to the queue", "error");
        });
        console.log(selectedQueue);
    
    }

    const handleChange = (id, event, type) => {
        const value = type === "Boolean" ? event.target.checked : parseInt(event.target.value);
        setFormValues(prev => ({ ...prev, [id]: value }));
    };

    const handleEvaluate = async (event) => {
        if (selectedQueue === undefined) {
            showAlert("Please select a queue first", "error");
            return;
        }

        showAlert("Evaluating...", "info");
        event.preventDefault();
        const arr = [];
        for (const [key, value] of Object.entries(formValues)) {
            arr.push({ scoring_form_item_id: key, answer: value });
        }

        const response = await apiService.post(`/queue/${selectedQueue}/evaluate/`, arr)
        showAlert("Evaluation completed successfully", "success");
        setEvalStats({ score: response.total_points, rank: response.rank, availability: response.approximate_availability });
        console.log(response);

    };

    const closeAlert = () => {
        setAlert({ visible: false, message: "", type: "" });
    }

    const showAlert = (message, type) => {
        setAlert({ visible: true, message, type });

        setTimeout(() => {
            setAlert({ visible: false, message: "", type: "" });
        }, 5000);
    }



    return (
    <div className="container flex justify-center mx-auto h-max items-center min-h-screen">
        {alert.visible && <MyAlert message={alert.message} type={alert.type} onClose={closeAlert} visible={alert.visible} />}
        <div className="p-5 my-10 shadow-md w-7/12 items-center flex justify-center flex-col">
            <div className="flex align-items-center items-center w-11/12 ">
                <label>Başvuracağınız kategoriyi seçiniz</label>
                <Select label="Select Version" id="queueSelect" value={selectedQueue} onChange={(val) => {
                    setSelectedQueue(val);
                    setOpen(1);
                }}>
                    {queueQuery?.data.map((lodgement) => (
                        <Option key={lodgement.id} value={lodgement.id}>
                            {lodgement.lodgement_type} - {lodgement.personel_type} - {lodgement.lodgement_size}
                        </Option>
                    ))}
                </Select>
            </div>

            <Accordion open={open === 1} className="py-6">
                <AccordionHeader onClick={() => handleOpen(1)}>Score Form</AccordionHeader>
                <AccordionBody className="font-normal text-lg">
                    <div className="flex flex-col">

                        <div className="w-12/12 shadow mx-auto flex flex-col">
                            <List>
                                {scoreFormQuery.data?.map((item) => (
                                    <ListItem key={item.id} className="w-full">
                                        <div className="flex justify-between w-full items-center">
                                            <div className="flex flex-row items-center">

                                                <Tooltip
                                                    content={
                                                        <div className="w-80">
                                                            {item.caption}
                                                        </div>
                                                    }
                                                    placement="top">

                                                    <label className=" ">{item.label}</label>
                                                </Tooltip>
                                            </div>
                                            <div>
                                                {item.field_type === "Integer" ? (
                                                    <Input
                                                        type="number"
                                                        value={formValues[item.id] || ''}
                                                        onChange={(e) => handleChange(item.id, e, item.field_type)}
                                                        className="input input-bordered"
                                                    />
                                                ) : (
                                                    <Checkbox
                                                        checked={formValues[item.id]}
                                                        onChange={(e) => handleChange(item.id, e, item.field_type)}
                                                        color="blue"
                                                    />
                                                )}
                                            </div>
                                        </div>
                                    </ListItem>
                                ))}
                            </List>
                            <Button variant="outlined" onClick={handleEvaluate} className="w-1/3 block ml-auto mr-0 py-4 mt-4 mb-6">Evaluate</Button>
                        </div>
                        <div className="flex flex-col justify-items-start">
                            <label className="pt-6">Your current score: {evalStats.score}</label>
                            <label className="pt-6">Your current rank: {evalStats.rank}</label>
                            <label className="pt-6">Approximate availability in: {evalStats.availability}</label>
                        </div>
                    </div>
                </AccordionBody>
            </Accordion>



            <Button variant="" color='green' className="w-full py-4 mt-5 text-base " onClick={applyQueue}> Apply</Button>
        </div>
    </div>);
}

export default ApplyPage;