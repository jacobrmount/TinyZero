/**
 * Remedy Notification Demo App
 * 
 * This is a mockup of how the Remedy app would handle notifications
 * For demonstration purposes only
 */

import React, { useState, useEffect } from 'react';
import {
  SafeAreaView,
  StyleSheet,
  View,
  Text,
  FlatList,
  TouchableOpacity,
  Switch,
  Image,
  Platform,
  Alert,
} from 'react-native';

// Mock Firebase messaging
const mockFirebaseMessaging = {
  requestPermission: () => Promise.resolve(true),
  getToken: () => Promise.resolve('fcm-token-123456789'),
  onMessage: (callback) => {
    // Simulate receiving a message after 5 seconds
    setTimeout(() => {
      callback({
        notification: {
          title: 'Bitcoin Price Alert',
          body: 'Bitcoin has reached $50,000!',
        },
        data: {
          type: 'event_alert',
          event_type: 'price_alert',
          threshold: '50000',
          currency: 'USD',
          id: '12345678',
          timestamp: '2023-08-15T14:30:00Z',
        },
      });
    }, 5000);
    return () => {}; // Return unsubscribe function
  },
};

// Demo App Component
const App = () => {
  const [notifications, setNotifications] = useState([]);
  const [isPermissionGranted, setIsPermissionGranted] = useState(false);
  const [token, setToken] = useState(null);
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);

  // Request permissions on app start
  useEffect(() => {
    const requestPermissions = async () => {
      try {
        const permission = await mockFirebaseMessaging.requestPermission();
        setIsPermissionGranted(permission);
        
        if (permission) {
          const fcmToken = await mockFirebaseMessaging.getToken();
          setToken(fcmToken);
          console.log('FCM Token:', fcmToken);
        }
      } catch (error) {
        console.error('Error requesting notification permissions:', error);
      }
    };
    
    requestPermissions();
  }, []);
  
  // Listen for incoming messages
  useEffect(() => {
    if (isPermissionGranted) {
      const unsubscribe = mockFirebaseMessaging.onMessage((message) => {
        console.log('New notification received:', message);
        
        if (notificationsEnabled) {
          const newNotification = {
            id: message.data.id || String(Date.now()),
            title: message.notification.title,
            body: message.notification.body,
            timestamp: message.data.timestamp || new Date().toISOString(),
            read: false,
            data: message.data,
          };
          
          setNotifications((prevNotifications) => 
            [newNotification, ...prevNotifications]
          );
          
          if (Platform.OS === 'ios') {
            // Simulate iOS local notification
            Alert.alert(
              message.notification.title,
              message.notification.body,
              [{ text: 'OK' }]
            );
          }
        }
      });
      
      // Cleanup subscription
      return unsubscribe;
    }
  }, [isPermissionGranted, notificationsEnabled]);
  
  // Render notification item
  const renderNotificationItem = ({ item }) => {
    const iconName = item.data && item.data.type === 'event_alert' 
      ? '🔔' : item.data && item.data.type === 'reminder_alert' 
      ? '⏰' : '📱';
    
    return (
      <TouchableOpacity
        style={[styles.notificationItem, item.read ? styles.readNotification : styles.unreadNotification]}
        onPress={() => markAsRead(item.id)}
      >
        <Text style={styles.notificationIcon}>{iconName}</Text>
        <View style={styles.notificationContent}>
          <Text style={styles.notificationTitle}>{item.title}</Text>
          <Text style={styles.notificationBody}>{item.body}</Text>
          <Text style={styles.notificationTime}>
            {new Date(item.timestamp).toLocaleString()}
          </Text>
        </View>
      </TouchableOpacity>
    );
  };
  
  // Mark notification as read
  const markAsRead = (id) => {
    setNotifications((prevNotifications) =>
      prevNotifications.map((notification) =>
        notification.id === id
          ? { ...notification, read: true }
          : notification
      )
    );
  };
  
  // Toggle notifications
  const toggleNotifications = () => {
    setNotificationsEnabled(!notificationsEnabled);
  };
  
  // Simulate receiving a test notification
  const receiveTestNotification = () => {
    if (notificationsEnabled) {
      mockFirebaseMessaging.onMessage({
        notification: {
          title: 'Test Notification',
          body: 'This is a test notification from Remedy',
        },
        data: {
          type: 'test',
          id: String(Date.now()),
          timestamp: new Date().toISOString(),
        },
      });
    } else {
      Alert.alert(
        'Notifications Disabled',
        'Please enable notifications to receive test messages',
        [{ text: 'OK' }]
      );
    }
  };
  
  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Remedy</Text>
        <View style={styles.notificationToggle}>
          <Text style={styles.toggleLabel}>Notifications</Text>
          <Switch
            value={notificationsEnabled}
            onValueChange={toggleNotifications}
            trackColor={{ false: '#767577', true: '#81b0ff' }}
            thumbColor={notificationsEnabled ? '#0066cc' : '#f4f3f4'}
          />
        </View>
      </View>
      
      {!isPermissionGranted ? (
        <View style={styles.permissionContainer}>
          <Text style={styles.permissionText}>
            Please enable notification permissions for Remedy to receive alerts
          </Text>
          <TouchableOpacity
            style={styles.permissionButton}
            onPress={() => mockFirebaseMessaging.requestPermission().then(setIsPermissionGranted)}
          >
            <Text style={styles.permissionButtonText}>Enable Notifications</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <>
          <View style={styles.deviceInfo}>
            <Text style={styles.deviceInfoText}>
              Device registered with FCM
            </Text>
            <Text style={styles.tokenText}>
              Token: {token ? `${token.substring(0, 8)}...${token.substring(token.length - 8)}` : 'Loading...'}
            </Text>
          </View>
          
          <TouchableOpacity
            style={styles.testButton}
            onPress={receiveTestNotification}
          >
            <Text style={styles.testButtonText}>Receive Test Notification</Text>
          </TouchableOpacity>
          
          <View style={styles.notificationListContainer}>
            <Text style={styles.sectionTitle}>Notification History</Text>
            
            {notifications.length === 0 ? (
              <View style={styles.emptyState}>
                <Text style={styles.emptyStateText}>
                  No notifications yet. Test notifications will appear here.
                </Text>
              </View>
            ) : (
              <FlatList
                data={notifications}
                renderItem={renderNotificationItem}
                keyExtractor={(item) => item.id}
                style={styles.notificationList}
              />
            )}
          </View>
        </>
      )}
    </SafeAreaView>
  );
};

// Styles
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 16,
    paddingHorizontal: 20,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#EEEEEE',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333333',
  },
  notificationToggle: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  toggleLabel: {
    marginRight: 8,
    color: '#666666',
  },
  permissionContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  permissionText: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 20,
    color: '#666666',
  },
  permissionButton: {
    backgroundColor: '#0066CC',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
  },
  permissionButtonText: {
    color: '#FFFFFF',
    fontWeight: 'bold',
    fontSize: 16,
  },
  deviceInfo: {
    padding: 16,
    backgroundColor: '#E8F4FE',
    marginHorizontal: 16,
    marginTop: 16,
    borderRadius: 8,
  },
  deviceInfoText: {
    fontSize: 14,
    color: '#333333',
    marginBottom: 4,
  },
  tokenText: {
    fontSize: 12,
    color: '#666666',
  },
  testButton: {
    backgroundColor: '#0066CC',
    marginHorizontal: 16,
    marginTop: 16,
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  testButtonText: {
    color: '#FFFFFF',
    fontWeight: 'bold',
    fontSize: 15,
  },
  notificationListContainer: {
    flex: 1,
    marginTop: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginHorizontal: 16,
    marginBottom: 8,
    color: '#333333',
  },
  notificationList: {
    flex: 1,
  },
  notificationItem: {
    flexDirection: 'row',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#EEEEEE',
    backgroundColor: '#FFFFFF',
  },
  unreadNotification: {
    backgroundColor: '#F0F7FF',
  },
  readNotification: {
    backgroundColor: '#FFFFFF',
  },
  notificationIcon: {
    fontSize: 24,
    marginRight: 16,
  },
  notificationContent: {
    flex: 1,
  },
  notificationTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333333',
    marginBottom: 4,
  },
  notificationBody: {
    fontSize: 14,
    color: '#666666',
    marginBottom: 4,
  },
  notificationTime: {
    fontSize: 12,
    color: '#999999',
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  emptyStateText: {
    textAlign: 'center',
    color: '#999999',
    fontSize: 15,
  },
});

export default App; 