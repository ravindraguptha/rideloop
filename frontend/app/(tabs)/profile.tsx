import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ScrollView,
} from 'react-native';
import { useAuth } from '../../contexts/AuthContext';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

export default function ProfileScreen() {
  const { user, logout } = useAuth();
  const router = useRouter();

  const handleLogout = () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Logout',
          style: 'destructive',
          onPress: async () => {
            await logout();
            router.replace('/');
          },
        },
      ]
    );
  };

  const menuItems = [
    { id: 'edit', title: 'Edit Profile', icon: 'person-outline', route: '/edit-profile' },
    { id: 'kyc', title: 'KYC Verification', icon: 'shield-checkmark-outline', route: '/kyc' },
    { id: 'vehicles', title: 'My Vehicles', icon: 'car-outline', route: '/vehicles', showForDriver: true },
    { id: 'trips', title: 'My Trips', icon: 'list-outline', route: '/(tabs)/dashboard' },
    { id: 'earnings', title: 'Earnings', icon: 'wallet-outline', route: '/earnings', showForDriver: true },
    { id: 'settings', title: 'Settings', icon: 'settings-outline', route: '/settings' },
    { id: 'support', title: 'Support', icon: 'help-circle-outline', route: '/support' },
  ];

  return (
    <ScrollView style={styles.container}>
      <View style={styles.profileCard}>
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>
            {user?.name.charAt(0).toUpperCase()}
          </Text>
        </View>

        <Text style={styles.name}>{user?.name}</Text>
        <Text style={styles.phone}>{user?.phone}</Text>

        {user?.kyc_verified && (
          <View style={styles.kycBadge}>
            <Ionicons name="shield-checkmark" size={16} color="#4CAF50" />
            <Text style={styles.kycText}>KYC Verified</Text>
          </View>
        )}

        <View style={styles.infoSection}>
          <View style={styles.infoCard}>
            <Text style={styles.infoLabel}>Role</Text>
            <Text style={styles.infoValue}>{user?.role || 'Passenger'}</Text>
          </View>
          {user?.gender && (
            <View style={styles.infoCard}>
              <Text style={styles.infoLabel}>Gender</Text>
              <Text style={styles.infoValue}>{user?.gender}</Text>
            </View>
          )}
        </View>
      </View>

      <View style={styles.menuSection}>
        {menuItems.map((item) => {
          // Filter menu items based on role
          if (item.showForDriver && user?.role !== 'Driver') {
            return null;
          }

          return (
            <TouchableOpacity
              key={item.id}
              style={styles.menuItem}
              onPress={() => router.push(item.route as any)}
            >
              <View style={styles.menuItemLeft}>
                <Ionicons name={item.icon as any} size={24} color="#4CAF50" />
                <Text style={styles.menuItemText}>{item.title}</Text>
              </View>
              <Ionicons name="chevron-forward" size={24} color="#999" />
            </TouchableOpacity>
          );
        })}
      </View>

      <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
        <Text style={styles.logoutButtonText}>Logout</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 16,
  },
  profileCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 24,
    alignItems: 'center',
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#4CAF50',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  avatarText: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#fff',
  },
  name: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  phone: {
    fontSize: 16,
    color: '#666',
    marginBottom: 24,
  },
  infoSection: {
    width: '100%',
  },
  infoCard: {
    backgroundColor: '#f9f9f9',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  infoLabel: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  infoValue: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  section: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  sectionText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  logoutButton: {
    backgroundColor: '#f44336',
    padding: 18,
    borderRadius: 8,
    alignItems: 'center',
    minHeight: 56,
    justifyContent: 'center',
  },
  logoutButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
});