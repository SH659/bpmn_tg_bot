import React, {useEffect, useState} from 'react';
import axios from "axios";

function BotsManager() {
    const [bots, setBots] = useState([]);
    const [selectedBotId, setSelectedBotId] = useState(null);
    const [formState, setFormState] = useState({
        name: '',
        token: '',
        diagram_id: '',
        run_on_startup: false,
    });

    // Fetch the list of bots on component mount
    useEffect(() => {
        listBots().then(
            () => console.log('Bots list fetched'),
        );
    }, []);

    const listBots = async () => {
        const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/bot/tg/`);
        setBots(response.data);
    };

    const handleFormChange = (e) => {
        const {name, value, type, checked} = e.target;
        setFormState(prevState => ({
            ...prevState,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const createOrUpdateBot = async (e) => {
        e.preventDefault();
        const method = selectedBotId ? 'put' : 'post';
        const endpoint = (
            selectedBotId ?
                `${process.env.REACT_APP_BACKEND_URL}/bot/tg/${selectedBotId}` :
                `${process.env.REACT_APP_BACKEND_URL}/bot/tg/`
            )
        await axios[method](endpoint, formState, {
            headers: {
                'Content-Type': 'application/json',
            },
        });
        await listBots(); // Refresh the list
        setFormState({name: '', token: '', diagram_id: '', run_on_startup: false}); // Reset form
        setSelectedBotId(null); // Reset selection
    };

    const selectBot = async (botId) => {
        const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/bot/tg/${botId}`);
        setFormState(response.data);
        setSelectedBotId(botId);
    };

    const deleteBot = async (botId) => {
        await axios.delete(`${process.env.REACT_APP_BACKEND_URL}/bot/tg/${botId}`);
        await listBots(); // Refresh the list
    };

    const controlBot = async (botId, action) => {
        await axios.post(`${process.env.REACT_APP_BACKEND_URL}/bot/tg/${botId}/${action}`);
        await listBots(); // To reflect any potential changes
    };

    return (<div>
            <h2>Bots Manager</h2>
            <form onSubmit={createOrUpdateBot} className="mb-3">
                <div className="mb-3">
                    <input
                        type="text"
                        className="form-control"
                        name="name"
                        value={formState.name}
                        onChange={handleFormChange}
                        placeholder="Bot Name"
                        required
                    />
                </div>
                <div className="mb-3">
                    <input
                        type="text"
                        className="form-control"
                        name="token"
                        value={formState.token}
                        onChange={handleFormChange}
                        placeholder="Bot Token"
                    />
                </div>
                <div className="mb-3">
                    <input
                        type="text"
                        className="form-control"
                        name="diagram_id"
                        value={formState.diagram_id}
                        onChange={handleFormChange}
                        placeholder="Diagram ID"
                    />
                </div>
                <div className="form-check mb-3">
                    <input
                        type="checkbox"
                        className="form-check-input"
                        name="run_on_startup"
                        id="runOnStartup"
                        checked={formState.run_on_startup}
                        onChange={handleFormChange}
                    />
                    <label className="form-check-label" htmlFor="runOnStartup">
                        Run on Startup
                    </label>
                </div>
                <button type="submit" className="btn btn-primary">Save Bot</button>
            </form>
            <ul>
                {bots.map(bot => (
                    <li key={bot.id} className="list-unstyled">
                        {bot.name} -
                        <button className="btn btn-secondary ms-2" onClick={() => selectBot(bot.id)}>Edit</button>
                        <button className="btn btn-danger ms-2" onClick={() => deleteBot(bot.id)}>Delete</button>
                        <button className="btn btn-success ms-2" onClick={() => controlBot(bot.id, 'run')}>Run</button>
                        <button className="btn btn-warning ms-2" onClick={() => controlBot(bot.id, 'stop')}>Stop
                        </button>
                        <button className="btn btn-info ms-2" onClick={() => controlBot(bot.id, 'restart')}>Restart
                        </button>
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default BotsManager;
