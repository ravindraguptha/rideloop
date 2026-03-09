import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  RefreshControl,
  TouchableOpacity,
} from 'react-native';
import Constants from 'expo-constants';
import { useAuth } from '../../contexts/AuthContext';

const API_URL = Constants.expoConfig?.extra?.EXPO_BACKEND_URL || '';

interface CreatedRide {
  id: string;
  start_location: string;
  destination: string;
  date: string;
  time: string;
  available_seats: number;
  total_seats: number;
  price_per_seat: number;
  status: string;
  passengers: Array<{
    name: string;
    phone: string;
    seats: number;
  }>;
}

interface JoinedRide {
  id: string;
  creator_name: string;
  creator_phone: string;
  start_location: string;
  destination: string;
  date: string;
  time: string;
  seats_booked: number;
  price_per_seat: number;
  status: string;
}

export default function DashboardScreen() {
  const [createdRides, setCreatedRides] = useState<CreatedRide[]>([]);
  const [joinedRides, setJoinedRides] = useState<JoinedRide[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState<'created' | 'joined'>('created');
  const { token } = useAuth();

  useEffect(() => {
    fetchMyRides();
  }, []);

  const fetchMyRides = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/my-rides?token=${token}`);
      if (response.ok) {
        const data = await response.json();
        setCreatedRides(data.created);
        setJoinedRides(data.joined);
      }
    } catch (error) {
      console.error('Error fetching rides:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    fetchMyRides();
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
      <View style={styles.tabContainer}>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'created' && styles.activeTab]}
          onPress={() => setActiveTab('created')}
        >
          <Text style={[styles.tabText, activeTab === 'created' && styles.activeTabText]}>
            Created ({createdRides.length})
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'joined' && styles.activeTab]}
          onPress={() => setActiveTab('joined')}
        >
          <Text style={[styles.tabText, activeTab === 'joined' && styles.activeTabText]}>
            Joined ({joinedRides.length})
          </Text>
        </TouchableOpacity>
      </View>

      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={['#4CAF50']} />
        }
      >
        {activeTab === 'created' ? (
          createdRides.length === 0 ? (
            <View style={styles.emptyState}>
              <Text style={styles.emptyText}>No rides created yet</Text>
              <Text style={styles.emptySubtext}>Create your first ride!</Text>
            </View>
          ) : (
            createdRides.map(ride => (
              <View key={ride.id} style={styles.rideCard}>
                <View style={styles.rideHeader}>
                  <Text style={styles.rideRoute}>
                    {ride.start_location} → {ride.destination}
                  </Text>
                  <View style={styles.statusBadge}>
                    <Text style={styles.statusText}>{ride.status}</Text>
                  </View>
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
                    <Text style={styles.detailLabel}>Seats:</Text>
                    <Text style={styles.detailValue}>
                      {ride.available_seats} / {ride.total_seats} available
                    </Text>
                  </View>
                  <View style={styles.detailRow}>
                    <Text style={styles.detailLabel}>Price:</Text>
                    <Text style={styles.detailValue}>₹{ride.price_per_seat} per seat</Text>
                  </View>
                </View>

                {ride.passengers.length > 0 && (
                  <View style={styles.passengersSection}>
                    <Text style={styles.passengersTitle}>Passengers:</Text>
                    {ride.passengers.map((passenger, index) => (
                      <View key={index} style={styles.passengerItem}>
                        <Text style={styles.passengerName}>{passenger.name}</Text>
                        <Text style={styles.passengerSeats}>{passenger.seats} seat(s)</Text>
                      </View>
                    ))}
                  </View>
                )}
              </View>
            ))
          )
        ) : (
          joinedRides.length === 0 ? (
            <View style={styles.emptyState}>
              <Text style={styles.emptyText}>No rides joined yet</Text>
              <Text style={styles.emptySubtext}>Find and join rides!</Text>
            </View>
          ) : (
            joinedRides.map(ride => (
              <View key={ride.id} style={styles.rideCard}>
                <View style={styles.rideHeader}>
                  <Text style={styles.rideRoute}>
                    {ride.start_location} → {ride.destination}
                  </Text>
                  <View style={styles.statusBadge}>
                    <Text style={styles.statusText}>{ride.status}</Text>
                  </View>
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
                    <Text style={styles.detailLabel}>Your Seats:</Text>
                    <Text style={styles.detailValue}>{ride.seats_booked}</Text>
                  </View>
                  <View style={styles.detailRow}>
                    <Text style={styles.detailLabel}>Total Cost:</Text>
                    <Text style={styles.detailValue}>
                      ₹{ride.price_per_seat * ride.seats_booked}
                    </Text>
                  </View>
                  <View style={styles.detailRow}>
                    <Text style={styles.detailLabel}>Driver:</Text>
                    <Text style={styles.detailValue}>{ride.creator_name}</Text>
                  </View>
                  <View style={styles.detailRow}>
                    <Text style={styles.detailLabel}>Contact:</Text>
                    <Text style={styles.detailValue}>{ride.creator_phone}</Text>
                  </View>
                </View>
              </View>
            ))
          )
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
  tabContainer: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  tab: {
    flex: 1,
    paddingVertical: 16,
    alignItems: 'center',
    borderBottomWidth: 2,
    borderBottomColor: 'transparent',
  },
  activeTab: {
    borderBottomColor: '#4CAF50',
  },
  tabText: {
    fontSize: 16,
    color: '#666',
    fontWeight: '500',
  },
  activeTabText: {
    color: '#4CAF50',
    fontWeight: 'bold',
  },
  content: {
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
  statusBadge: {
    backgroundColor: '#e8f5e9',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    color: '#4CAF50',
    fontSize: 12,
    fontWeight: '600',
    textTransform: 'capitalize',
  },
  rideDetails: {
    marginBottom: 12,
  },
  detailRow: {
    flexDirection: 'row',
    marginBottom: 8,
  },
  detailLabel: {
    fontSize: 14,
    color: '#666',
    width: 100,
  },
  detailValue: {
    fontSize: 14,
    color: '#333',
    fontWeight: '500',
    flex: 1,
  },
  passengersSection: {
    marginTop: 16,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
  },
  passengersTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  passengerItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 6,
    paddingHorizontal: 12,
    backgroundColor: '#f5f5f5',
    borderRadius: 6,
    marginBottom: 4,
  },
  passengerName: {
    fontSize: 14,
    color: '#333',
  },
  passengerSeats: {
    fontSize: 14,
    color: '#666',
  },
});