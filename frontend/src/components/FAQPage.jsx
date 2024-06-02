import React, { useState } from 'react';
import {
    Accordion,
    AccordionHeader,
    AccordionBody,
    Typography,
} from '@material-tailwind/react';
import { useQuery } from '@tanstack/react-query';
import { apiService } from '../services/apiService';
import DOMPurify from 'dompurify';


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
                F.A.Q.
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
                        <div variant="div" className="font-normal contents text-blue-gray-900" dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(item.answer) }}>
                            
                        </div>
                    </AccordionBody>
                </Accordion>
            ))}
        </div>
    );
};

export default FAQ;