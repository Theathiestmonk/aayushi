import React from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Mail, CheckCircle, ArrowLeft } from 'lucide-react';

const EmailConfirmation: React.FC = () => {
  const [searchParams] = useSearchParams();
  const email = searchParams.get('email') || 'your email';

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        {/* Header */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="w-20 h-20 bg-gradient-to-r from-blue-500 to-green-500 rounded-full mx-auto mb-4 flex items-center justify-center"
          >
            <Mail className="w-10 h-10 text-white" />
          </motion.div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Check Your Email
          </h1>
          <p className="text-gray-600">
            We've sent a confirmation link to
          </p>
          <p className="text-blue-600 font-medium text-lg mt-2">
            {email}
          </p>
        </div>

        {/* Confirmation Message */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100"
        >
          <div className="text-center space-y-6">
            {/* Success Icon */}
            <div className="w-16 h-16 bg-green-100 rounded-full mx-auto flex items-center justify-center">
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>

            {/* Message */}
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Almost Done!
              </h2>
              <p className="text-gray-600 leading-relaxed">
                Click the confirmation link in your email to activate your account. 
                Once confirmed, you'll be able to sign in and start your health journey.
              </p>
            </div>

            {/* Email Tips */}
            <div className="bg-blue-50 rounded-lg p-4 text-left">
              <h3 className="font-medium text-blue-900 mb-2">📧 Email Tips:</h3>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• Check your spam/junk folder if you don't see it</li>
                <li>• The email should arrive within a few minutes</li>
                <li>• Click the "Confirm Email" button in the email</li>
                <li>• Make sure to check the email address you used</li>
              </ul>
            </div>

            {/* Action Buttons */}
            <div className="space-y-3">
              <Link
                to="/login"
                className="w-full inline-flex items-center justify-center px-4 py-3 border border-transparent rounded-lg text-sm font-medium text-white bg-gradient-to-r from-blue-500 to-green-500 hover:from-blue-600 hover:to-green-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200"
              >
                Go to Sign In
              </Link>
              
              <Link
                to="/register"
                className="w-full inline-flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Registration
              </Link>
            </div>
          </div>
        </motion.div>

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.6 }}
          className="mt-8 text-center text-sm text-gray-500"
        >
          <p>
            Didn't receive the email?{' '}
            <Link to="/register" className="text-blue-600 hover:underline">
              Try registering again
            </Link>
          </p>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default EmailConfirmation;

