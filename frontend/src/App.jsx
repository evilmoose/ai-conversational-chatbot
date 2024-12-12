import { /*useState*,*/ useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux';
import { setConversations } from './store/chatSlice';
import './App.css'

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
    <div>
      <h1>Conversations</h1>
      <ul>
        {conversations.map((conv, index) => (
          <li key={index}>{conv.prompt}: {conv.response}</li>
        ))}
      </ul>
    </div>
  )
}

export default App
