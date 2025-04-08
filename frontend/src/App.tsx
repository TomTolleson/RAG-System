import React, { useState, useEffect, useRef } from 'react';
import { 
  Container, 
  Box, 
  Typography, 
  TextField, 
  Button, 
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  AppBar,
  Toolbar,
  Drawer,
  Divider,
  CircularProgress
} from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon, Send as SendIcon, Upload as UploadIcon } from '@mui/icons-material';
import axios, { AxiosError } from 'axios';

interface Message {
  text: string;
  isUser: boolean;
}

interface Space {
  name: string;
  documents: string[];
}

interface ErrorResponse {
  detail: string;
}

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [spaces, setSpaces] = useState<Space[]>([]);
  const [currentSpace, setCurrentSpace] = useState<string>('default');
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [newSpaceDialog, setNewSpaceDialog] = useState(false);
  const [newSpaceName, setNewSpaceName] = useState('');
  const [newSpaceDocuments, setNewSpaceDocuments] = useState<string[]>([]);
  const [uploadDialog, setUploadDialog] = useState(false);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetchSpaces();
  }, []);

  const fetchSpaces = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/spaces`);
      setSpaces(response.data.spaces.map((name: string) => ({ name, documents: [] })));
    } catch (error) {
      console.error('Error fetching spaces:', error);
    }
  };

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = input;
    setInput('');
    setMessages(prev => [...prev, { text: userMessage, isUser: true }]);

    try {
      const response = await axios.post(`${API_BASE_URL}/spaces/${currentSpace}/query`, {
        query: userMessage,
        space_name: currentSpace
      });
      
      const results = response.data.results || [];
      if (results.length > 0) {
        setMessages(prev => [...prev, { 
          text: results[0].text || 'No results found.', 
          isUser: false 
        }]);
      } else {
        setMessages(prev => [...prev, { 
          text: 'No results found.', 
          isUser: false 
        }]);
      }
    } catch (err) {
      console.error('Error sending message:', err);
      const error = err as Error;
      if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError<ErrorResponse>;
        setMessages(prev => [...prev, { 
          text: `Error: ${axiosError.response?.data?.detail || axiosError.message}`, 
          isUser: false 
        }]);
      } else {
        setMessages(prev => [...prev, { 
          text: `Error: ${error.message || 'Sorry, there was an error processing your request.'}`, 
          isUser: false 
        }]);
      }
    }
  };

  const handleCreateSpace = async () => {
    if (!newSpaceName.trim()) {
      alert('Please enter a space name');
      return;
    }

    // Validate space name according to ChromaDB requirements
    const spaceName = newSpaceName.trim();
    const isValidName = /^[a-zA-Z0-9][a-zA-Z0-9_-]{1,61}[a-zA-Z0-9]$/.test(spaceName) && 
                       !spaceName.includes('..') && 
                       !/^\d+\.\d+\.\d+\.\d+$/.test(spaceName);

    if (!isValidName) {
      alert('Invalid space name. Please follow these rules:\n\n' +
            '1. Must be between 3 and 63 characters long\n' +
            '2. Must start with a letter or number\n' +
            '3. Must end with a letter or number\n' +
            '4. Can only contain letters, numbers, underscores (_), or hyphens (-)\n' +
            '5. Cannot contain consecutive periods (..)\n' +
            '6. Cannot be a valid IPv4 address\n\n' +
            'Examples of valid names:\n' +
            '- my-space\n' +
            '- test123\n' +
            '- project_1');
      return;
    }

    try {
      const response = await axios.post(`${API_BASE_URL}/spaces`, {
        name: spaceName,
        documents: [{
          text: "Welcome to your new space!",
          metadata: {
            type: "welcome",
            created_at: new Date().toISOString(),
            source: "system"
          }
        }]
      });
      
      setNewSpaceDialog(false);
      setNewSpaceName('');
      setNewSpaceDocuments([]);
      fetchSpaces();
    } catch (error) {
      console.error('Error creating space:', error);
      if (axios.isAxiosError(error)) {
        alert(`Failed to create space: ${error.response?.data?.detail || error.message}`);
      } else {
        alert('Failed to create space. Please try again.');
      }
    }
  };

  const handleDeleteSpace = async (spaceName: string) => {
    if (spaceName === 'default') {
      alert('Cannot delete the default space');
      return;
    }

    if (!window.confirm(`Are you sure you want to delete the space "${spaceName}"?`)) {
      return;
    }

    try {
      await axios.delete(`${API_BASE_URL}/spaces/${spaceName}`);
      if (currentSpace === spaceName) {
        setCurrentSpace('default');
      }
      fetchSpaces();
    } catch (error) {
      console.error('Error deleting space:', error);
      if (axios.isAxiosError(error)) {
        alert(`Failed to delete space: ${error.response?.data?.detail || error.message}`);
      } else {
        alert('Failed to delete space. Please try again.');
      }
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      await axios.post(`${API_BASE_URL}/api/spaces/${currentSpace}/documents`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      alert('Document uploaded successfully!');
      setUploadDialog(false);
    } catch (error) {
      console.error('Error uploading document:', error);
      if (axios.isAxiosError(error)) {
        alert(`Failed to upload document: ${error.response?.data?.detail || error.message}`);
      } else {
        alert('Failed to upload document. Please try again.');
      }
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <Typography variant="h6" noWrap component="div">
            RAG System
          </Typography>
        </Toolbar>
      </AppBar>
      
      <Drawer
        variant="permanent"
        sx={{
          width: 240,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: 240,
            boxSizing: 'border-box',
            marginTop: '64px'
          },
        }}
      >
        <Toolbar />
        <Box sx={{ overflow: 'auto' }}>
          <List>
            <ListItem>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setNewSpaceDialog(true)}
                fullWidth
              >
                New Space
              </Button>
            </ListItem>
            <Divider />
            {spaces.map((space) => (
              <ListItem
                button
                key={space.name}
                selected={currentSpace === space.name}
                onClick={() => setCurrentSpace(space.name)}
              >
                <ListItemText primary={space.name} />
                <ListItemSecondaryAction>
                  <IconButton 
                    edge="end" 
                    aria-label="delete"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteSpace(space.name);
                    }}
                  >
                    <DeleteIcon />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        </Box>
      </Drawer>

      <Box component="main" sx={{ flexGrow: 1, p: 3, marginTop: '64px' }}>
        <Container maxWidth="lg">
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h5">
              {currentSpace}
            </Typography>
            <Button
              variant="contained"
              startIcon={<UploadIcon />}
              onClick={() => setUploadDialog(true)}
            >
              Upload Document
            </Button>
          </Box>

          <Paper sx={{ height: '70vh', overflow: 'auto', mb: 2, p: 2 }}>
            {messages.map((message, index) => (
              <Box
                key={index}
                sx={{
                  display: 'flex',
                  justifyContent: message.isUser ? 'flex-end' : 'flex-start',
                  mb: 2
                }}
              >
                <Paper
                  sx={{
                    p: 2,
                    maxWidth: '70%',
                    backgroundColor: message.isUser ? '#e3f2fd' : '#f5f5f5'
                  }}
                >
                  <Typography>{message.text}</Typography>
                </Paper>
              </Box>
            ))}
          </Paper>
          
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Type your message..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  handleSendMessage();
                }
              }}
            />
            <Button
              variant="contained"
              endIcon={<SendIcon />}
              onClick={handleSendMessage}
            >
              Send
            </Button>
          </Box>
        </Container>
      </Box>

      <Dialog open={newSpaceDialog} onClose={() => setNewSpaceDialog(false)}>
        <DialogTitle>Create New Space</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Space Name"
            fullWidth
            value={newSpaceName}
            onChange={(e) => setNewSpaceName(e.target.value)}
          />
          <TextField
            margin="dense"
            label="Document Paths (one per line)"
            fullWidth
            multiline
            rows={4}
            value={newSpaceDocuments.join('\n')}
            onChange={(e) => setNewSpaceDocuments(e.target.value.split('\n'))}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setNewSpaceDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateSpace} variant="contained">Create</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={uploadDialog} onClose={() => setUploadDialog(false)}>
        <DialogTitle>Upload Document to {currentSpace}</DialogTitle>
        <DialogContent>
          <input
            type="file"
            ref={fileInputRef}
            style={{ display: 'none' }}
            onChange={handleFileChange}
          />
          <Button
            variant="contained"
            component="span"
            onClick={handleUploadClick}
            disabled={uploading}
            sx={{ mt: 2 }}
          >
            {uploading ? <CircularProgress size={24} /> : 'Select File'}
          </Button>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUploadDialog(false)}>Cancel</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default App; 