import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export default function SettingsScreen() {
  return (
    <ScrollView style={styles.container}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Preferences</Text>
        <TouchableOpacity style={styles.item}>
          <View style={styles.itemLeft}>
            <Ionicons name="notifications-outline" size={24} color="#4CAF50" />
            <Text style={styles.itemText}>Notifications</Text>
          </View>
          <Ionicons name="chevron-forward" size={24} color="#999" />
        </TouchableOpacity>
        <TouchableOpacity style={styles.item}>
          <View style={styles.itemLeft}>
            <Ionicons name="language-outline" size={24} color="#4CAF50" />
            <Text style={styles.itemText}>Language</Text>
          </View>
          <Ionicons name="chevron-forward" size={24} color="#999" />
        </TouchableOpacity>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Account</Text>
        <TouchableOpacity style={styles.item}>
          <View style={styles.itemLeft}>
            <Ionicons name="lock-closed-outline" size={24} color="#4CAF50" />
            <Text style={styles.itemText}>Privacy</Text>
          </View>
          <Ionicons name="chevron-forward" size={24} color="#999" />
        </TouchableOpacity>
        <TouchableOpacity style={styles.item}>
          <View style={styles.itemLeft}>
            <Ionicons name="shield-outline" size={24} color="#4CAF50" />
            <Text style={styles.itemText}>Security</Text>
          </View>
          <Ionicons name="chevron-forward" size={24} color="#999" />
        </TouchableOpacity>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>App Info</Text>
        <View style={styles.item}>
          <View style={styles.itemLeft}>
            <Ionicons name="information-circle-outline" size={24} color="#4CAF50" />
            <Text style={styles.itemText}>Version</Text>
          </View>
          <Text style={styles.versionText}>1.0.0</Text>
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
  section: {
    backgroundColor: '#fff',
    marginTop: 16,
    paddingVertical: 8,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#999',
    paddingHorizontal: 16,
    paddingVertical: 12,
    textTransform: 'uppercase',
  },
  item: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 16,
    paddingHorizontal: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
    minHeight: 60,
  },
  itemLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 16,
  },
  itemText: {
    fontSize: 16,
    color: '#333',
  },
  versionText: {
    fontSize: 16,
    color: '#999',
  },
});