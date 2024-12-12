import { /*useState*,*/ useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { setConversations } from './store/chatSlice';
import Register from './pages/Register';
import Login from './pages/Login';
import Chat from './pages/Chat';
import './App.css';
import './portal.css';

function App() {
  //const [count, setCount] = useState(0)
  const dispatch = useDispatch();
  const conversations = useSelector((state) => state.chat.conversations);

  useEffect(() => {
    fetch('/chat/conversations')
      .then((response) => response.json())
      .then((data) => dispatch(setConversations(data)));
  }, [dispatch]);

  return (
    <Router>
      <Routes>
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route
          path="/chat"
          element={
            <Chat conversations={conversations} />
          }
        />
      </Routes>
    </Router>
  );
};

export default App
