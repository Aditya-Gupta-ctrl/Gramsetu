import React, { useState } from 'react';
import { View, StyleSheet, Text, TouchableOpacity, Alert } from 'react-native';
import { Audio } from 'expo-av';
import { Camera } from 'expo-camera';
import { Button, Card, Title, Paragraph } from 'react-native-paper';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export default function App() {
    const [recording, setRecording] = useState(null);
    const [jobId, setJobId] = useState(null);
    const [status, setStatus] = useState('Ready');

    // Request permissions
    const requestPermissions = async () => {
        const audioPermission = await Audio.requestPermissionsAsync();
        const cameraPermission = await Camera.requestCameraPermissionsAsync();

        if (!audioPermission.granted || !cameraPermission.granted) {
            Alert.alert('Permissions Required', 'Please grant audio and camera permissions');
        }
    };

    React.useEffect(() => {
        requestPermissions();
    }, []);

    // Start voice recording
    const startRecording = async () => {
        try {
            await Audio.setAudioModeAsync({
                allowsRecordingIOS: true,
                playsInSilentModeIOS: true,
            });

            const { recording } = await Audio.Recording.createAsync(
                Audio.RecordingOptionsPresets.HIGH_QUALITY
            );
            setRecording(recording);
            setStatus('Recording...');
        } catch (err) {
            console.error('Failed to start recording', err);
        }
    };

    // Stop and process recording
    const stopRecording = async () => {
        setStatus('Processing voice...');
        setRecording(undefined);
        await recording.stopAndUnloadAsync();

        const uri = recording.getURI();

        // Convert to base64
        const base64Audio = await FileSystem.readAsStringAsync(uri, {
            encoding: FileSystem.EncodingType.Base64,
        });

        // Send to voice service
        try {
            const response = await axios.post(`${API_BASE_URL}/jobs`, {
                vle_id: 'VLE001',
                citizen_name: 'Unknown', // Will be extracted from voice
                citizen_phone: '+919876543210',
                consent_recorded: true,
                voice_input: {
                    audio_base64: base64Audio,
                    vle_id: 'VLE001',
                    language_hint: 'hi'
                }
            });

            setJobId(response.data.job_id);
            setStatus(`Job created: ${response.data.job_id}`);

            // Start polling for status
            pollJobStatus(response.data.job_id);
        } catch (error) {
            setStatus('Error: ' + error.message);
        }
    };

    // Poll job status
    const pollJobStatus = async (jobId) => {
        const interval = setInterval(async () => {
            try {
                const response = await axios.get(`${API_BASE_URL}/jobs/${jobId}`);
                setStatus(`Status: ${response.data.status}`);

                if (response.data.status === 'completed' || response.data.status === 'failed') {
                    clearInterval(interval);
                    if (response.data.status === 'completed') {
                        Alert.alert('Success', 'Application processed successfully!');
                    }
                }
            } catch (error) {
                clearInterval(interval);
                setStatus('Error polling status');
            }
        }, 2000);
    };

    return (
        <View style={styles.container}>
            <Card style={styles.card}>
                <Card.Content>
                    <Title>GramSetu VLE App</Title>
                    <Paragraph>Voice-first government service assistant</Paragraph>
                </Card.Content>
            </Card>

            <View style={styles.statusContainer}>
                <Text style={styles.statusText}>{status}</Text>
            </View>

            <View style={styles.buttonContainer}>
                <Button
                    mode="contained"
                    onPress={recording ? stopRecording : startRecording}
                    style={styles.button}
                    icon={recording ? 'stop' : 'microphone'}
                >
                    {recording ? 'Stop Recording' : 'Start Recording'}
                </Button>

                <Button
                    mode="outlined"
                    onPress={() => {/* TODO: Open camera for document scan */ }}
                    style={styles.button}
                    icon="camera"
                >
                    Scan Document
                </Button>
            </View>

            {jobId && (
                <Card style={styles.jobCard}>
                    <Card.Content>
                        <Title>Job ID</Title>
                        <Paragraph>{jobId}</Paragraph>
                    </Card.Content>
                </Card>
            )}
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f5f5f5',
        padding: 20,
        justifyContent: 'center',
    },
    card: {
        marginBottom: 20,
    },
    statusContainer: {
        backgroundColor: '#e3f2fd',
        padding: 15,
        borderRadius: 8,
        marginBottom: 20,
    },
    statusText: {
        fontSize: 16,
        color: '#1976d2',
        textAlign: 'center',
    },
    buttonContainer: {
        gap: 10,
    },
    button: {
        marginVertical: 5,
    },
    jobCard: {
        marginTop: 20,
        backgroundColor: '#e8f5e9',
    },
});
