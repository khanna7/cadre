import { initializeApp } from 'firebase/app';
import { getFirestore } from 'firebase/firestore';
import { getStorage } from 'firebase/storage';
import {
  getAuth,
  onAuthStateChanged,
  GoogleAuthProvider,
  signInWithPopup,
} from 'firebase/auth';
import firebase from 'firebase/compat/app';

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_LOGIN_API_KEY,
  authDomain: 'meyers-lab.firebaseapp.com',
  projectId: 'meyers-lab',
  storageBucket: 'meyers-lab.appspot.com',
  messagingSenderId: process.env.NEXT_PUBLIC_APP_MSG,
  appId: process.env.NEXT_PUBLIC_APP_APP,
  measurementId: process.env.NEXT_PUBLIC_APP_MSR,
};


  const app = initializeApp(firebaseConfig);
  const firestore = getFirestore(app);
  const storage = getStorage(app);
  const auth = getAuth(app)

  export { firestore, storage, auth };

