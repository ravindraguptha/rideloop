import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
} from 'react-native';
import { useAuth } from '../contexts/AuthContext';
import { Ionicons } from '@expo/vector-icons';
import Constants from 'expo-constants';

const API_URL = Constants.expoConfig?.extra?.EXPO_BACKEND_URL || '';

export default function EarningsScreen() {
  const { token } = useAuth();
  const [loading, setLoading] = useState(false);
  const [earnings, setEarnings] = useState({
    total_earnings: 0,
    completed_trips: 0,
    rides_created: 0,
  });

  useEffect(() => {
    fetchEarnings();
  }, []);

  const fetchEarnings = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/earnings?token=${token}`);
      if (response.ok) {
        const data = await response.json();
        setEarnings(data);
      }
    } catch (error) {
      console.error('Error fetching earnings:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#4CAF50" />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Ionicons name="wallet" size={48} color="#4CAF50" />
        <Text style={styles.totalAmount}>₹{earnings.total_earnings.toFixed(2)}</Text>
        <Text style={styles.totalLabel}>Total Earnings</Text>
      </View>

      <View style={styles.statsContainer}>
        <View style={styles.statCard}>
          <Ionicons name="car" size={32} color="#4CAF50" />
          <Text style={styles.statValue}>{earnings.rides_created}</Text>
          <Text style={styles.statLabel}>Rides Created</Text>
        </View>

        <View style={styles.statCard}>
          <Ionicons name="checkmark-circle" size={32} color="#4CAF50" />
          <Text style={styles.statValue}>{earnings.completed_trips}</Text>
          <Text style={styles.statLabel}>Completed</Text>
        </View>
      </View>

      <View style={styles.infoSection}>
        <Text style={styles.infoTitle}>How Earnings Work</Text>
        <View style={styles.infoItem}>
          <Ionicons name="information-circle-outline" size={20} color="#666" />
          <Text style={styles.infoText}>
            Earnings are calculated from accepted ride bookings
          </Text>
        </View>
        <View style={styles.infoItem}>
          <Ionicons name="information-circle-outline" size={20} color="#666" />
          <Text style={styles.infoText}>
            Price per seat × number of passengers = trip earnings
          </Text>
        </View>
        <View style={styles.infoItem}>
          <Ionicons name="information-circle-outline" size={20} color="#666" />
          <Text style={styles.infoText}>
            All amounts shown are before any platform fees
          </Text>
        </View>
      </View>
    </ScrollView>
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
  header: {
    backgroundColor: '#fff',
    padding: 32,
    alignItems: 'center',
    marginBottom: 16,
  },
  totalAmount: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#4CAF50',
    marginTop: 16,
  },
  totalLabel: {
    fontSize: 16,
    color: '#666',
    marginTop: 8,
  },
  statsContainer: {
    flexDirection: 'row',
    padding: 16,
    gap: 16,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 12,
    alignItems: 'center',
  },
  statValue: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 12,
  },
  statLabel: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  infoSection: {
    backgroundColor: '#fff',
    margin: 16,
    padding: 20,
    borderRadius: 12,
  },
  infoTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
  },
  infoItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 12,
    gap: 12,
  },
  infoText: {
    flex: 1,
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
});