import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { Picker } from '@react-native-picker/picker';
import Constants from 'expo-constants';
import { useAuth } from '../../contexts/AuthContext';
import { useRouter } from 'expo-router';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

const API_URL = Constants.expoConfig?.extra?.EXPO_BACKEND_URL || '';

const LOCATIONS = [
  'Gachibowli',
  'Hitech City',
  'Madhapur',
  'Kukatpally',
  'Ameerpet',
  'Banjara Hills',
  'Jubilee Hills',
  'Begumpet',
  'Secunderabad',
  'Kondapur',
  'Miyapur',
  'LB Nagar',
  'Uppal',
  'Dilsukhnagar',
  'Charminar',
  'Mehdipatnam',
  'Tarnaka',
  'Koti',
  'Somajiguda',
  'Nagole',
];

export default function CreateRideScreen() {
  const [startLocation, setStartLocation] = useState(LOCATIONS[0]);
  const [destination, setDestination] = useState(LOCATIONS[1]);
  const [date, setDate] = useState('');
  const [time, setTime] = useState('');
  const [seats, setSeats] = useState('');
  const [price, setPrice] = useState('');
  const [loading, setLoading] = useState(false);
  const { token } = useAuth();
  const router = useRouter();
  const insets = useSafeAreaInsets();

  const handleCreateRide = async () => {
    if (!date || !time || !seats || !price) {
      Alert.alert('Error', 'Please fill all fields');
      return;
    }

    if (startLocation === destination) {
      Alert.alert('Error', 'Start location and destination cannot be the same');
      return;
    }

    const seatsNum = parseInt(seats);
    const priceNum = parseFloat(price);

    if (isNaN(seatsNum) || seatsNum < 1 || seatsNum > 8) {
      Alert.alert('Error', 'Please enter valid number of seats (1-8)');
      return;
    }

    if (isNaN(priceNum) || priceNum < 0) {
      Alert.alert('Error', 'Please enter valid price');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/rides?token=${token}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          start_location: startLocation,
          destination,
          date,
          time,
          available_seats: seatsNum,
          price_per_seat: priceNum,
        }),
      });

      if (response.ok) {
        Alert.alert('Success', 'Ride created successfully!', [
          {
            text: 'OK',
            onPress: () => {
              setDate('');
              setTime('');
              setSeats('');
              setPrice('');
              router.push('/(tabs)/dashboard');
            },
          },
        ]);
      } else {
        const error = await response.json();
        Alert.alert('Error', error.detail || 'Failed to create ride');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to create ride');
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.form}>
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Start Location</Text>
            <View style={styles.pickerWrapper}>
              <Picker
                selectedValue={startLocation}
                onValueChange={setStartLocation}
                style={styles.picker}
              >
                {LOCATIONS.map(loc => (
                  <Picker.Item key={loc} label={loc} value={loc} />
                ))}
              </Picker>
            </View>
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Destination</Text>
            <View style={styles.pickerWrapper}>
              <Picker
                selectedValue={destination}
                onValueChange={setDestination}
                style={styles.picker}
              >
                {LOCATIONS.map(loc => (
                  <Picker.Item key={loc} label={loc} value={loc} />
                ))}
              </Picker>
            </View>
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Date (DD/MM/YYYY)</Text>
            <TextInput
              style={styles.input}
              placeholder="e.g., 25/07/2025"
              value={date}
              onChangeText={setDate}
            />
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Time (HH:MM AM/PM)</Text>
            <TextInput
              style={styles.input}
              placeholder="e.g., 09:00 AM"
              value={time}
              onChangeText={setTime}
            />
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Available Seats</Text>
            <TextInput
              style={styles.input}
              placeholder="Number of seats (1-8)"
              value={seats}
              onChangeText={setSeats}
              keyboardType="number-pad"
            />
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Price per Seat (₹)</Text>
            <TextInput
              style={styles.input}
              placeholder="Enter price"
              value={price}
              onChangeText={setPrice}
              keyboardType="decimal-pad"
            />
          </View>

          <TouchableOpacity
            style={[styles.button, loading && styles.buttonDisabled]}
            onPress={handleCreateRide}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.buttonText}>Create Ride</Text>
            )}
          </TouchableOpacity>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollContent: {
    padding: 16,
  },
  form: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
  },
  inputGroup: {
    marginBottom: 20,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  pickerWrapper: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    backgroundColor: '#f9f9f9',
  },
  picker: {
    height: 50,
  },
  input: {
    backgroundColor: '#f9f9f9',
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 16,
    fontSize: 16,
    minHeight: 56,
  },
  button: {
    backgroundColor: '#4CAF50',
    padding: 18,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 8,
    minHeight: 56,
    justifyContent: 'center',
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
});