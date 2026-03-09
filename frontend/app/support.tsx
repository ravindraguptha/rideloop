import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Linking,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export default function SupportScreen() {
  const handleEmail = () => {
    Linking.openURL('mailto:support@rideloop.com');
  };

  const handlePhone = () => {
    Linking.openURL('tel:+911234567890');
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Ionicons name="help-circle" size={64} color="#4CAF50" />
        <Text style={styles.title}>How can we help?</Text>
        <Text style={styles.subtitle}>Get in touch with our support team</Text>
      </View>

      <View style={styles.section}>
        <TouchableOpacity style={styles.contactCard} onPress={handleEmail}>
          <View style={styles.iconCircle}>
            <Ionicons name="mail-outline" size={28} color="#4CAF50" />
          </View>
          <View style={styles.contactInfo}>
            <Text style={styles.contactLabel}>Email Us</Text>
            <Text style={styles.contactValue}>support@rideloop.com</Text>
          </View>
          <Ionicons name="chevron-forward" size={24} color="#999" />
        </TouchableOpacity>

        <TouchableOpacity style={styles.contactCard} onPress={handlePhone}>
          <View style={styles.iconCircle}>
            <Ionicons name="call-outline" size={28} color="#4CAF50" />
          </View>
          <View style={styles.contactInfo}>
            <Text style={styles.contactLabel}>Call Us</Text>
            <Text style={styles.contactValue}>+91 1234567890</Text>
          </View>
          <Ionicons name="chevron-forward" size={24} color="#999" />
        </TouchableOpacity>
      </View>

      <View style={styles.faqSection}>
        <Text style={styles.faqTitle}>Frequently Asked Questions</Text>
        
        <View style={styles.faqItem}>
          <Text style={styles.faqQuestion}>How do I create a ride?</Text>
          <Text style={styles.faqAnswer}>
            Go to the Create tab, fill in your ride details, and publish your ride.
          </Text>
        </View>

        <View style={styles.faqItem}>
          <Text style={styles.faqQuestion}>How do payments work?</Text>
          <Text style={styles.faqAnswer}>
            Payments are handled directly between riders. We display total cost for transparency.
          </Text>
        </View>

        <View style={styles.faqItem}>
          <Text style={styles.faqQuestion}>Can I cancel a ride?</Text>
          <Text style={styles.faqAnswer}>
            Contact the driver/passenger directly to discuss cancellations.
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
  header: {
    backgroundColor: '#fff',
    padding: 32,
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 16,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginTop: 8,
  },
  section: {
    padding: 16,
  },
  contactCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
  },
  iconCircle: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#e8f5e9',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  contactInfo: {
    flex: 1,
  },
  contactLabel: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  contactValue: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  faqSection: {
    backgroundColor: '#fff',
    padding: 20,
    marginTop: 8,
  },
  faqTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 20,
  },
  faqItem: {
    marginBottom: 20,
  },
  faqQuestion: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  faqAnswer: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
});