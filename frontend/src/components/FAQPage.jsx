import React, { useState } from 'react';
import {
    Accordion,
    AccordionHeader,
    AccordionBody,
    Typography,
} from '@material-tailwind/react';
import { useQuery } from '@tanstack/react-query';
import { apiService } from '../services/apiService';


const FAQ = () => {
    const [open, setOpen] = useState(null);

    const { data: faqData, isLoading, error } = useQuery(['faq'], () => apiService.get('/faq/'));

    const handleOpen = (value) => {
        setOpen(open === value ? null : value);
    };


    if (isLoading) {
        return <div>Loading...</div>;
    }
    if (error) {
        return <div>Error: {error.message}</div>;
    }



    return (
        <div className="w-full mx-auto mt-20">
            <Typography variant="h2" color="blue-gray" className="mb-8 mt-8 font-bold">
                Sıkça Sorulan Sorular
            </Typography>
            {faqData.sort((a, b) => a.order - b.order).map((item, index) => (
                <Accordion
                    key={index}
                    open={open === index}
                >
                    <AccordionHeader onClick={() => handleOpen(index)}>
                        <Typography variant="h5" color="blue-gray" className="font-normal">
                            {item.question}
                        </Typography>
                    </AccordionHeader>
                    <AccordionBody>
                        <Typography variant="p" color="blue-gray" className="font-normal">
                            {item.answer}
                        </Typography>
                    </AccordionBody>
                </Accordion>
            ))}
        </div>
    );
};

export default FAQ;