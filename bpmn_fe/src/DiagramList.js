import React, {useEffect, useState} from 'react';
import axios from 'axios';
import {useNavigate} from 'react-router-dom';
import { Button, ListGroup } from 'react-bootstrap';

const DiagramList = () => {
    const [diagrams, setDiagrams] = useState([]);
    const navigate = useNavigate();

    const createNewDiagram = async () => {
        try {
            const response = await axios.post(`${process.env.REACT_APP_BACKEND_URL}/diagrams/`, {});
            const newDiagramId = response.data.id;
            navigate(`/editor/${newDiagramId}`);
        } catch (error) {
            console.error('Failed to create new diagram:', error);
        }
    };

    useEffect(() => {
        const fetchDiagrams = async () => {
            const result = await axios(`${process.env.REACT_APP_BACKEND_URL}/diagrams/`);
            setDiagrams(result.data);
        };
        fetchDiagrams();
    }, []);

    return (
        <div className="container py-4">
            <h1 className="mb-4">Diagrams</h1>
            <Button variant="primary" onClick={createNewDiagram}>New Diagram</Button>
            <ListGroup className="mt-3">
                {diagrams.map(diagram => (
                    <ListGroup.Item action key={diagram.id} onClick={() => navigate(`/editor/${diagram.id}`)}>
                        {diagram.name ?? diagram.id}
                    </ListGroup.Item>
                ))}
            </ListGroup>
        </div>
    );
};

export default DiagramList;
