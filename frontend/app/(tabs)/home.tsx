import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { Picker } from '@react-native-picker/picker';
import Constants from 'expo-constants';
import { useAuth } from '../../contexts/AuthContext';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import Toast from 'react-native-toast-message';
import { HYDERABAD_LOCATIONS } from '../../constants/Locations';
import { Colors } from '../../constants/Colors';

const API_URL = Constants.expoConfig?.extra?.EXPO_BACKEND_URL || '';

const LOCATIONS = HYDERABAD_LOCATIONS;

interface Ride {
  id: string;
  creator_name: string;
  creator_phone: string;
  start_location: string;
  destination: string;
  date: string;
  time: string;
  available_seats: number;
  total_seats: number;
  price_per_seat: number;
}

export default function HomeScreen() {
  const [rides, setRides] = useState<Ride[]>([]);
  const [filteredRides, setFilteredRides] = useState<Ride[]>([]);
  const [startLocation, setStartLocation] = useState('All');
  const [destination, setDestination] = useState('All');
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const { token } = useAuth();
  const insets = useSafeAreaInsets();

  useEffect(() => {
    fetchRides();
  }, []);

  useEffect(() => {
    filterRides();
  }, [rides, startLocation, destination]);

  const fetchRides = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/rides`);
      if (response.ok) {
        const data = await response.json();
        setRides(data);
      }
    } catch (error) {
      console.error('Error fetching rides:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const filterRides = () => {
    let filtered = rides;
    if (startLocation !== 'All') {
      filtered = filtered.filter(r => r.start_location === startLocation);
    }
    if (destination !== 'All') {
      filtered = filtered.filter(r => r.destination === destination);
    }
    setFilteredRides(filtered);
  };

  const handleJoinRide = async (rideId: string) => {
    if (!token) {
      Toast.show({
        type: 'error',
        text1: 'Authentication Required',
        text2: 'Please login to join rides',
      });
      return;
    }

    Alert.alert(
      'Join Ride',
      'Do you want to book 1 seat in this ride?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Join',
          onPress: async () => {
            try {
              const response = await fetch(`${API_URL}/api/rides/${rideId}/join?token=${token}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ seats: 1 }),
              });

              if (response.ok) {
                Toast.show({
                  type: 'success',
                  text1: 'Request Sent!',
                  text2: 'Ride request sent successfully',
                });
                fetchRides();
              } else {
                const error = await response.json();
                Toast.show({
                  type: 'error',
                  text1: 'Error',
                  text2: error.detail || 'Failed to join ride',
                });
              }
            } catch (error) {
              Toast.show({
                type: 'error',
                text1: 'Error',
                text2: 'Failed to join ride',
              });
            }
          },
        },
      ]
    );
  };

  const onRefresh = () => {
    setRefreshing(true);
    fetchRides();
  };

  if (loading && !refreshing) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#4CAF50" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.filterSection}>
        <View style={styles.pickerContainer}>
          <Text style={styles.pickerLabel}>From</Text>
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

        <View style={styles.pickerContainer}>
          <Text style={styles.pickerLabel}>To</Text>
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
      </View>

      <ScrollView
        style={styles.ridesList}
        contentContainerStyle={{ paddingBottom: insets.bottom + 70 }}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={['#4CAF50']} />
        }
      >
        {filteredRides.length === 0 ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyText}>No rides available</Text>
            <Text style={styles.emptySubtext}>Try adjusting your filters</Text>
          </View>
        ) : (
          filteredRides.map(ride => (
            <View key={ride.id} style={styles.rideCard}>
              <View style={styles.rideHeader}>
                <Text style={styles.rideRoute}>
                  {ride.start_location} → {ride.destination}
                </Text>
                <Text style={styles.ridePrice}>₹{ride.price_per_seat}</Text>
              </View>

              <View style={styles.rideDetails}>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Date:</Text>
                  <Text style={styles.detailValue}>{ride.date}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Time:</Text>
                  <Text style={styles.detailValue}>{ride.time}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Available Seats:</Text>
                  <Text style={styles.detailValue}>
                    {ride.available_seats} / {ride.total_seats}
                  </Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Driver:</Text>
                  <Text style={styles.detailValue}>{ride.creator_name}</Text>
                </View>
              </View>

              <TouchableOpacity
                style={styles.joinButton}
                onPress={() => handleJoinRide(ride.id)}
              >
                <Text style={styles.joinButtonText}>Join Ride</Text>
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
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  filterSection: {
    backgroundColor: Colors.white,
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  pickerContainer: {
    marginBottom: 12,
  },
  pickerLabel: {
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
  ridesList: {
    flex: 1,
    padding: 16,
  },
  emptyState: {
    alignItems: 'center',
    marginTop: 48,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#666',
  },
  emptySubtext: {
    fontSize: 14,
    color: '#999',
    marginTop: 8,
  },
  rideCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  rideHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
    paddingBottom: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  rideRoute: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    flex: 1,
  },
  ridePrice: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#4CAF50',
  },
  rideDetails: {
    marginBottom: 16,
  },
  detailRow: {
    flexDirection: 'row',
    marginBottom: 8,
  },
  detailLabel: {
    fontSize: 14,
    color: '#666',
    width: 120,
  },
  detailValue: {
    fontSize: 14,
    color: '#333',
    fontWeight: '500',
    flex: 1,
  },
  joinButton: {
    backgroundColor: Colors.primary,
    padding: 14,
    borderRadius: 8,
    alignItems: 'center',
    minHeight: 48,
    justifyContent: 'center',
  },
  joinButtonText: {
    color: Colors.white,
    fontSize: 16,
    fontWeight: 'bold',
  },
});