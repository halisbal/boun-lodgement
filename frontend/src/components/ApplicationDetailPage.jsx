import { List, ListItem, Input, Checkbox, Button, Card, Select, Option } from "@material-tailwind/react";
import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { useEffect } from "react";
import { useState } from "react";
import fetchApplicationDetail from "../fetchs/fetchApplicationDetail";


const ApplicationDetailPage = () => {

    const { id } = useParams();
    const { data, status, error } = useQuery(['applicationDetail', id], () => fetchApplicationDetail(id));

    const [formValues, setFormValues] = useState({});
    const [selectedDocument, setSelectedDocument] = useState();

    // Initialize form values when data is loaded
    useEffect(() => {
        const initialValues = {};
        data?.scoring_form?.items.forEach(item => {
            initialValues[item.id] = item.answer ? item.answer.value : '';
        });
        setFormValues(initialValues);
    }, [data]);

    if (status === 'loading') return <div>Loading...</div>;
    if (status === 'error') return <div>Error: {error.message}</div>;
    if (!data) return <div>No data found.</div>;

    const handleChange = (id, event, type) => {
        const value = type === "Boolean" ? event.target.checked : event.target.value;
        setFormValues(prev => ({ ...prev, [id]: value }));
    };

    const handleSubmit = (event) => {
        event.preventDefault();
        console.log("Submitting", formValues);
        // Here you would typically use fetch or axios to send `formValues` to the server
    };

    const handleFileChange = (event) => {
        const file = event.target.files[0];
        console.log("File selected", file);
        // Here you would typically use fetch or axios to send `file` to the server
    }

    return (
        <div className="bg-gray-100">
            <div>

            </div>

            <span className="m-4 p-4"><label className="text-3xl">BAŞVURU CETVELİ</label></span>

            <div className="flex flex-col items-center mt-6">
                <Card className="w-8/12 shadow">
                    <List>
                        {data.scoring_form.items.map((item) => (
                            <ListItem key={item.id} className="w-full">
                                <div className="flex justify-between w-full items-center">
                                    <div>
                                        <label className="">{item.label}</label>
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
                                                checked={!!formValues[item.id]}
                                                onChange={(e) => handleChange(item.id, e, item.field_type)}
                                                color="blue"
                                            />
                                        )}
                                    </div>
                                </div>
                            </ListItem>
                        ))}
                    </List>
                    <Button type="submit" className="w-6/12 mx-auto py-4 mt-4 mb-6">Submit</Button>
                </Card>


            </div>

            <div className="flex mt-6 w-full flex-col  rounded-xl items-center">

                <div className="flex shadow bg-white p-4 items-center justify-between w-8/12 mx-auto ">
                    <div>
                        <label>Yükleyeceğiniz dosyayı seçiniz</label>
                    </div>
                    <div className="w-1/2">
                        <Select label="Select Version" id="documentSelect" value={selectedDocument} onChange={(val) => setSelectedDocument(val)}>
                            {data?.queue?.required_documents?.map((document) => (
                                <Option key={document.id} value={document.id}>
                                    {document.name}
                                </Option>
                            ))}
                        </Select>
                    </div>


                </div>

                <div className="flex items-center bg-white justify-center w-8/12">
                    <label htmlFor="dropzone-file" className="flex flex-col items-center justify-center w-full h-64 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 dark:hover:bg-bray-800 dark:bg-gray-700 hover:bg-gray-100 dark:border-gray-600 dark:hover:border-gray-500 dark:hover:bg-gray-600">
                        <div className="flex flex-col items-center justify-center pt-5 pb-6">
                            <svg className="w-8 h-8 mb-4 text-gray-500 dark:text-gray-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 16">
                                <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2" />
                            </svg>
                            <p className="mb-2 text-sm text-gray-500 dark:text-gray-400"><span className="font-semibold">Click to upload</span> or drag and drop</p>
                            <p className="text-xs text-gray-500 dark:text-gray-400">SVG, PNG, JPG or GIF (MAX. 800x400px)</p>
                        </div>
                        <input id="dropzone-file" type="file" className="hidden" onChange={handleFileChange}/>
                    </label>
                </div>
                <Button className="w-1/3 p-4 my-6" color="green">Upload</Button>


            </div>
        </div>
    );
}

export default ApplicationDetailPage;