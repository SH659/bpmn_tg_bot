import React, { useEffect, useRef, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import BpmnModeler from 'bpmn-js/lib/Modeler';
import customModule from "./customModule";
import 'bootstrap/dist/css/bootstrap.min.css'; // Import Bootstrap CSS

const DiagramEditor = () => {
    const { diagramId } = useParams();
    const modelerRef = useRef(null);
    const modelerInstance = useRef(null);
    const [diagramName, setDiagramName] = useState('');
    const [isEditingName, setIsEditingName] = useState(false);

    useEffect(() => {
        if (!modelerInstance.current && modelerRef.current) {
            modelerInstance.current = new BpmnModeler({
                container: modelerRef.current,
                additionalModules: [customModule],
            });
        }
    }, [diagramId]);

    useEffect(() => {
        const fetchAndLoadDiagram = async () => {
            try {
                const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/diagrams/${diagramId}`);
                const { xml, name } = response.data; // Assuming name is part of the response
                await modelerInstance.current.importXML(xml);
                setDiagramName(name || 'New Diagram');
            } catch (error) {
                console.error('Failed to fetch or import diagram:', error);
            }
        };

        if (diagramId) {
            fetchAndLoadDiagram();
        }
    }, [diagramId]);

    const handleSave = async () => {
        if (!modelerInstance.current) {
            console.error('Modeler is not initialized');
            return;
        }

        modelerInstance.current.saveXML({ format: true }).then(async ({ xml }) => {
            try {
                await axios.put(`${process.env.REACT_APP_BACKEND_URL}/diagrams/${diagramId}`, {
                    xml,
                    name: diagramName,
                });
            } catch (error) {
                console.error('Failed to save diagram:', error);
            }
        });
    };


    const handleNameChange = (e) => {
        if (e.key === 'Enter' || e.type === 'blur') {
            setIsEditingName(false);
            handleSave();
        }
    };

    return (
        <div className="container-fluid" style={{ height: '100vh' }}>
            <div className="row mb-2">
                <div className="col">
                    {isEditingName ? (
                        <input
                            type="text"
                            className="form-control"
                            value={diagramName}
                            onBlur={handleNameChange}
                            onKeyDown={(e) => e.key === 'Enter' && handleNameChange(e)}
                            onChange={(e) => setDiagramName(e.target.value)}
                            autoFocus
                        />
                    ) : (
                        <h3 onClick={() => setIsEditingName(true)} style={{ cursor: 'pointer' }}>
                            {diagramName || 'Click to set a diagram name'}
                        </h3>
                    )}
                </div>
                <div className="col-auto">
                    <button className="btn btn-primary" onClick={handleSave}>Save Diagram</button>
                </div>
            </div>
            <div ref={modelerRef} className="row" style={{ height: 'calc(100% - 38px)' }}></div>
        </div>
    );
};

export default DiagramEditor;
