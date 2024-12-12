import { createSlice } from '@reduxjs/toolkit';

const chatSlice = createSlice({
  name: 'chat',
  initialState: { conversations: [] },
  reducers: {
    setConversations: (state, action) => {
      state.conversations = action.payload;
    },
  },
});

export const { setConversations } = chatSlice.actions;
export default chatSlice.reducer;