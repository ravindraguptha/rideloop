import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useAuth } from '../contexts/AuthContext';
import { Ionicons } from '@expo/vector-icons';
import Constants from 'expo-constants';

const API_URL = Constants.expoConfig?.extra?.EXPO_BACKEND_URL || '';

interface Vehicle {
  id: string;
  vehicle_type: string;
  vehicle_number: string;
  vehicle_model: string;
  vehicle_color: string;
  accept_requests: boolean;
}

export default function VehiclesScreen() {
  const { token } = useAuth();
  const router = useRouter();
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  
  const [vehicleType, setVehicleType] = useState('');
  const [vehicleNumber, setVehicleNumber] = useState('');
  const [vehicleModel, setVehicleModel] = useState('');
  const [vehicleColor, setVehicleColor] = useState('');

  useEffect(() => {
    fetchVehicles();
  }, []);

  const fetchVehicles = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/vehicles?token=${token}`);
      if (response.ok) {
        const data = await response.json();
        setVehicles(data);
      }
    } catch (error) {
      console.error('Error fetching vehicles:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddVehicle = async () => {
    if (!vehicleType || !vehicleNumber || !vehicleModel || !vehicleColor) {
      Alert.alert('Error', 'Please fill all fields');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/vehicles?token=${token}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          vehicle_type: vehicleType,
          vehicle_number: vehicleNumber,
          vehicle_model: vehicleModel,
          vehicle_color: vehicleColor,
        }),
      });

      if (response.ok) {
        Alert.alert('Success', 'Vehicle added successfully');
        setShowForm(false);
        setVehicleType('');
        setVehicleNumber('');
        setVehicleModel('');
        setVehicleColor('');
        fetchVehicles();
      } else {
        Alert.alert('Error', 'Failed to add vehicle');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to add vehicle');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleAcceptRequests = async (vehicleId: string, currentStatus: boolean) => {
    try {
      const response = await fetch(`${API_URL}/api/vehicles/${vehicleId}?token=${token}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ accept_requests: !currentStatus }),
      });

      if (response.ok) {
        fetchVehicles();
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to update vehicle');
    }
  };

  const handleDeleteVehicle = async (vehicleId: string) => {
    Alert.alert(
      'Delete Vehicle',
      'Are you sure you want to delete this vehicle?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              const response = await fetch(`${API_URL}/api/vehicles/${vehicleId}?token=${token}`, {
                method: 'DELETE',
              });

              if (response.ok) {
                Alert.alert('Success', 'Vehicle deleted');
                fetchVehicles();
              } else {
                Alert.alert('Error', 'Failed to delete vehicle');
              }
            } catch (error) {
              Alert.alert('Error', 'Failed to delete vehicle');
            }
          },
        },
      ]
    );
  };

  return (
    <View style={styles.container}>
      <ScrollView style={styles.content}>
        {!showForm && (
          <TouchableOpacity
            style={styles.addButton}
            onPress={() => setShowForm(true)}
          >
            <Ionicons name="add-circle" size={24} color="#fff" />
            <Text style={styles.addButtonText}>Add Vehicle</Text>
          </TouchableOpacity>
        )}

        {showForm && (
          <View style={styles.form}>
            <Text style={styles.formTitle}>Add New Vehicle</Text>
            
            <TextInput
              style={styles.input}
              placeholder="Vehicle Type (e.g., Sedan, SUV)"
              value={vehicleType}
              onChangeText={setVehicleType}
            />
            <TextInput
              style={styles.input}
              placeholder="Vehicle Number (e.g., TS 09 AB 1234)"
              value={vehicleNumber}
              onChangeText={setVehicleNumber}
            />
            <TextInput
              style={styles.input}
              placeholder="Vehicle Model (e.g., Honda City)"
              value={vehicleModel}
              onChangeText={setVehicleModel}
            />
            <TextInput
              style={styles.input}
              placeholder="Color"
              value={vehicleColor}
              onChangeText={setVehicleColor}
            />

            <View style={styles.formButtons}>
              <TouchableOpacity
                style={[styles.button, loading && styles.buttonDisabled]}
                onPress={handleAddVehicle}
                disabled={loading}
              >
                <Text style={styles.buttonText}>Save</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.cancelButton}
                onPress={() => setShowForm(false)}
              >
                <Text style={styles.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>
            </View>
          </View>
        )}

        {loading && vehicles.length === 0 ? (
          <ActivityIndicator size="large" color="#4CAF50" style={{marginTop: 48}} />
        ) : vehicles.length === 0 ? (
          <View style={styles.emptyState}>
            <Ionicons name="car-outline" size={64} color="#ccc" />
            <Text style={styles.emptyText}>No vehicles added</Text>
          </View>
        ) : (
          vehicles.map((vehicle) => (
            <View key={vehicle.id} style={styles.vehicleCard}>
              <View style={styles.vehicleHeader}>
                <View>
                  <Text style={styles.vehicleNumber}>{vehicle.vehicle_number}</Text>
                  <Text style={styles.vehicleModel}>
                    {vehicle.vehicle_type} - {vehicle.vehicle_model}
                  </Text>
                  <Text style={styles.vehicleColor}>Color: {vehicle.vehicle_color}</Text>
                </View>
                <TouchableOpacity
                  onPress={() => handleDeleteVehicle(vehicle.id)}
                >
                  <Ionicons name="trash-outline" size={24} color="#f44336" />
                </TouchableOpacity>
              </View>

              <TouchableOpacity
                style={styles.toggleRow}
                onPress={() => handleToggleAcceptRequests(vehicle.id, vehicle.accept_requests)}
              >
                <Text style={styles.toggleLabel}>Accept Ride Requests</Text>
                <View
                  style={[
                    styles.toggle,
                    vehicle.accept_requests && styles.toggleActive,
                  ]}
                >
                  <View
                    style={[
                      styles.toggleThumb,
                      vehicle.accept_requests && styles.toggleThumbActive,
                    ]}
                  />
                </View>
              </TouchableOpacity>
            </View>
          ))
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  addButton: {
    flexDirection: 'row',
    backgroundColor: '#4CAF50',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
    gap: 8,
  },
  addButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  form: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
  },
  formTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 16,
    color: '#333',
  },
  input: {
    backgroundColor: '#f9f9f9',
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 16,
    fontSize: 16,
    marginBottom: 12,
    minHeight: 56,
  },
  formButtons: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 8,
  },
  button: {
    flex: 1,
    backgroundColor: '#4CAF50',
    padding: 14,
    borderRadius: 8,
    alignItems: 'center',
    minHeight: 48,
    justifyContent: 'center',
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  cancelButton: {
    flex: 1,
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#ddd',
    padding: 14,
    borderRadius: 8,
    alignItems: 'center',
    minHeight: 48,
    justifyContent: 'center',
  },
  cancelButtonText: {
    color: '#666',
    fontSize: 16,
    fontWeight: 'bold',
  },
  emptyState: {
    alignItems: 'center',
    marginTop: 48,
  },
  emptyText: {
    fontSize: 16,
    color: '#999',
    marginTop: 16,
  },
  vehicleCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  vehicleHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 16,
  },
  vehicleNumber: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  vehicleModel: {
    fontSize: 14,
    color: '#666',
    marginBottom: 2,
  },
  vehicleColor: {
    fontSize: 14,
    color: '#666',
  },
  toggleRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
  },
  toggleLabel: {
    fontSize: 14,
    color: '#333',
    fontWeight: '500',
  },
  toggle: {
    width: 51,
    height: 31,
    borderRadius: 16,
    backgroundColor: '#ddd',
    padding: 2,
    justifyContent: 'center',
  },
  toggleActive: {
    backgroundColor: '#4CAF50',
  },
  toggleThumb: {
    width: 27,
    height: 27,
    borderRadius: 14,
    backgroundColor: '#fff',
  },
  toggleThumbActive: {
    alignSelf: 'flex-end',
  },
});