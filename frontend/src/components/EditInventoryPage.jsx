import React, { useState, useEffect } from 'react';
import { useQuery, useQueryClient, useMutation } from "@tanstack/react-query";
import lodgementService from "../services/lodgementService";
import { Button, Alert, Dialog, DialogBody, DialogFooter, DialogHeader, Input, List, ListItem, Typography, Tooltip, IconButton, Select, Option } from '@material-tailwind/react';
import { PencilIcon } from "@heroicons/react/24/solid";
import LodgementList from './LodgementList';
import SortableTable from './SortableTable';
import fetchQueues from '../fetchs/fetchQueues.js';
import { apiService } from '../services/apiService';

const emptyLodgement = {
    name: "",
    size: "",
    description: "",
    location: "",
    is_available: "",
    queue_id: ""
};


const EditInventoryPage = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [selectedLodgementInfo, setSelectedLodgementInfo] = useState(emptyLodgement);

    const { data: lodgements, isLoading, error } = useQuery(["lodgementList"], lodgementService.getLodgementList);
    const { data: queues } = useQuery(["queueList"], fetchQueues);

    const queryClient = useQueryClient();

    console.log(lodgements)
    console.log(queues)
    console.log(selectedLodgementInfo)

    useEffect(() => {
        if (!isOpen) {
            setSelectedLodgementInfo(emptyLodgement); // Clear the selected item when dialog is closed
        }
    }, [isOpen]);


    const mutation = useMutation(
        (updatedLodgement) => apiService.patch(`/lodgement/${updatedLodgement.id}/`, updatedLodgement),
        {
          onSuccess: () => {
            queryClient.invalidateQueries("lodgementList");
            alert("Lodgement updated successfully.");
            setIsOpen(false);
          },
          onError: () => {
            alert("An error occurred. Please try again.");

          }
        }
      );

    const handleChange = (e) => {
        const { id, value } = e.target;
        setSelectedLodgementInfo((prevDetails) => ({
            ...prevDetails,
            [id]: value,
        }));
    };
    const handleSelectChange = (value) => {
        console.log(value)
        setSelectedLodgementInfo((prevDetails) => ({
            ...prevDetails,
            queue: queues.find((queue) => queue.id === value),
            queue_id: value
        }));
    };

    

    const handleSave = () => {
        console.log(selectedLodgementInfo);

        mutation.mutate(selectedLodgementInfo);

    };

    const handleOpen = (key) => {
        setIsOpen(true);
        console.log(lodgements)
        setSelectedLodgementInfo(lodgements.find((lodgement) => lodgement.id === key));

        console.log(key)
    }
    const handleClose = () => setIsOpen(false);

    if (isLoading) {
        return <p>Loading...</p>;
    }
    if (error) {
        return <p>Error: {error.message}</p>;
    }

    const TABLE_HEADERS = ["Name", "Size", "Description", "Location", "Is Available", "Queue ID", ""];

    return (
        <div className='w-2/3 mx-auto justify-center pt-4'>


            <table className="mt-4 w-full min-w-max table-auto text-left">
                <thead>
                    <tr className="cursor-pointer border-y border-blue-gray-100 bg-blue-gray-50/50 p-4 transition-colors hover:bg-blue-gray-50">

                        {TABLE_HEADERS.map((head, index) => (
                            <th key={head} className="cursor-pointer border-y border-blue-gray-100 bg-blue-gray-50/50 p-4 transition-colors hover:bg-blue-gray-50">
                                <Typography variant="small" color="blue-gray" className="flex items-center justify-between gap-2 font-normal leading-none opacity-70">
                                    {head}
                                </Typography>
                            </th>
                        ))}

                    </tr>
                </thead>
                <tbody>
                    {lodgements.map((lodgement, index) => {
                        const isLast = index === lodgements.length - 1;
                        const classes = isLast
                            ? "p-4"
                            : "p-4 border-b border-blue-gray-50";

                        return (
                            <tr key={lodgement.id}>
                                <td className={classes}>
                                    <div className="flex items-center gap-3">
                                        <Typography
                                            variant="small"
                                            color="blue-gray"
                                            className="font-normal"
                                        >
                                            {lodgement.name}
                                        </Typography>
                                    </div>
                                </td>
                                <td className={classes}>
                                    <Typography
                                        variant="small"
                                        color="blue-gray"
                                        className="font-normal"
                                    >
                                        {lodgement.size}
                                    </Typography>
                                </td>
                                <td className={classes}>
                                    <Typography
                                        variant="small"
                                        color="blue-gray"
                                        className="font-normal"
                                    >
                                        {lodgement.description}
                                    </Typography>
                                </td>
                                <td className={classes}>
                                    <Typography
                                        variant="small"
                                        color="blue-gray"
                                        className="font-normal"
                                    >
                                        {lodgement.location}
                                    </Typography>
                                </td>
                                <td className={classes}>
                                    <Typography
                                        variant="small"
                                        color="blue-gray"
                                        className="font-normal"
                                    >
                                        {lodgement.is_available}
                                    </Typography>
                                </td>

                                <td className={classes}>
                                    <Typography
                                        variant="small"
                                        color="blue-gray"
                                        className="font-normal"
                                    >
                                        {lodgement.queue.personel_type} - {lodgement.queue.lodgement_type} - {lodgement.queue.lodgement_size}
                                    </Typography>
                                </td>

                                <td className={classes}>
                                    <Tooltip content="Edit User">
                                        <IconButton variant="text" onClick={() => handleOpen(lodgement.id)}>
                                            <PencilIcon className="h-4 w-4" />
                                        </IconButton>
                                    </Tooltip>
                                </td>
                            </tr>);
                    })}

                </tbody>

            </table>

            <div>
                <Dialog size='xs' open={isOpen} handler={setIsOpen}>
                    <DialogHeader>burası header</DialogHeader>
                    <DialogBody >
                        <div className='py-2'>
                            <Input id='name' value={selectedLodgementInfo.name} onChange={handleChange} />
                        </div>
                        <div className='py-2'>
                            <Input id='size' value={selectedLodgementInfo.size} onChange={handleChange} />
                        </div>
                        <div className='py-2'>
                            <Input id='description' value={selectedLodgementInfo.description} onChange={handleChange} />
                        </div>
                        <div className='py-2'>
                            <Input id='location' value={selectedLodgementInfo.location} onChange={handleChange} />
                        </div>
                        <div className='py-2'>
                            <Input id='is_available' value={selectedLodgementInfo.is_available} onChange={handleChange} />
                        </div>
                        <div className='py-2'>
                            <Select value={selectedLodgementInfo.queue_id} onChange={(val) => handleSelectChange(val)}>
                                {queues.map((queue) =>
                                    <Option key={queue.id} value={queue.id}>{queue.personel_type} - {queue.lodgement_type} - {queue.lodgement_size}</Option>
                                )}
                            </Select>

                        </div>



                    </DialogBody>
                    <DialogFooter>
                        <Button color="red" onClick={handleClose}>Cancel</Button>
                        <Button color="blue" onClick={handleSave}>Save</Button>
                    </DialogFooter>
                </Dialog>
            </div>
        </div >
    );
};

export default EditInventoryPage;