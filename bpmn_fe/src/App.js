import {BrowserRouter as Router, Route, Routes} from 'react-router-dom';
import DiagramList from './DiagramList';
import DiagramEditor from './DiagramEditor';

const App = () => {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<DiagramList/>} exact/>
                <Route path="/editor/:diagramId" element={<DiagramEditor />} />
            </Routes>
        </Router>
    );
};

export default App