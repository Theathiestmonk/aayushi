import React, { useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Mail, CheckCircle, ArrowLeft, Lock, AlertCircle, Eye, EyeOff } from 'lucide-react'
import { supabase } from '@/lib/supabase'
import { apiPost } from '@/utils/api'

const ForgotPassword: React.FC = () => {
  const navigate = useNavigate()
  const [step, setStep] = useState<number>(1) // 1: Email, 2: OTP + Password
  const [formData, setFormData] = useState({
    email: '',
    otp: ['', '', '', '', '', ''] as string[],
    password: '',
    confirmPassword: ''
  })
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [error, setError] = useState<string>('')
  const [success, setSuccess] = useState<string>('')
  const [resendCooldown, setResendCooldown] = useState<number>(0)
  const [cooldownLogging, setCooldownLogging] = useState<boolean>(false)
  const [showPassword, setShowPassword] = useState<boolean>(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState<boolean>(false)
  const otpRefs = useRef<Array<HTMLInputElement | null>>([])

  useEffect(() => {
    if (resendCooldown > 0) {
      const timer = setTimeout(() => setResendCooldown(resendCooldown - 1), 1000)
      if (cooldownLogging) {
        console.log(`[ForgotPassword] Resend cooldown: ${resendCooldown}s remaining`)
      }
      return () => clearTimeout(timer)
    }
    if (cooldownLogging && resendCooldown === 0) {
      console.log('[ForgotPassword] Resend cooldown finished. Button enabled again.')
      setCooldownLogging(false)
    }
  }, [resendCooldown])

  const otpValue = useMemo(() => formData.otp.join(''), [formData.otp])
  const passwordsMatch = useMemo(() => formData.password !== '' && formData.password === formData.confirmPassword, [formData.password, formData.confirmPassword])
  const canSubmit = useMemo(
    () => !isLoading && otpValue.length === 6 && formData.password.length >= 6 && passwordsMatch,
    [isLoading, otpValue.length, formData.password.length, passwordsMatch]
  )

  const validateEmail = (email: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)

  const handleSendCode = async () => {
    try {
      setError('')
      setSuccess('')
      if (!validateEmail(formData.email)) {
        setError('Please enter a valid email address')
        return
      }
      setIsLoading(true)
      console.log('[ForgotPassword] Sending verification code to:', formData.email)
      // Prefer backend to ensure delivery with service role
      try {
        const resp = await apiPost('/auth/reset-password', { email: formData.email })
        if (!resp?.success) {
          throw new Error(resp?.error || 'Failed to send verification code')
        }
        console.log('[ForgotPassword] Backend responded success for:', formData.email)
      } catch (be) {
        // As a fallback, try client-side
        const { error: feError } = await supabase.auth.resetPasswordForEmail(formData.email, {
          redirectTo: `${window.location.origin}/reset-password`
        })
        if (feError) {
          setError(feError.message || 'Failed to send verification code')
          return
        }
        console.log('[ForgotPassword] Fallback client send success for:', formData.email)
      }
      setSuccess(`Verification code sent to ${formData.email}`)
      setStep(2)
      setResendCooldown(60)
      setCooldownLogging(true)
    } catch (e) {
      setError('Failed to send verification code')
    } finally {
      setIsLoading(false)
    }
  }

  const handleResend = async () => {
    if (resendCooldown > 0) return
    await handleSendCode()
  }

  const handleOTPChange = (index: number, value: string) => {
    if (!/^\d*$/.test(value)) return
    const newOTP = [...formData.otp]
    newOTP[index] = value
    setFormData(prev => ({ ...prev, otp: newOTP }))
    if (value && index < 5) {
      otpRefs.current[index + 1]?.focus()
    }
  }

  const handleOTPKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace' && !formData.otp[index] && index > 0) {
      otpRefs.current[index - 1]?.focus()
    }
  }

  const handleOTPPaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    e.preventDefault()
    const pastedData = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6)
    const newOTP = pastedData.split('').concat(Array(6 - pastedData.length).fill(''))
    setFormData(prev => ({ ...prev, otp: newOTP }))
    const lastFilledIndex = Math.min(pastedData.length - 1, 5)
    if (lastFilledIndex >= 0) otpRefs.current[lastFilledIndex]?.focus()
  }

  const handleResetPassword = async () => {
    try {
      setError('')
      setSuccess('')
      if (!validateEmail(formData.email)) {
        setError('Please enter a valid email address')
        return
      }
      if (otpValue.length !== 6) {
        setError('Please enter the 6-digit verification code')
        return
      }
      if (formData.password.length < 6) {
        setError('Password must be at least 6 characters')
        return
      }
      if (formData.password !== formData.confirmPassword) {
        setError('Passwords do not match')
        return
      }
      setIsLoading(true)
      const { error: verifyError } = await supabase.auth.verifyOtp({
        email: formData.email,
        token: otpValue,
        type: 'recovery'
      })
      if (verifyError) {
        // Fallback to backend confirm endpoint
        try {
          const resp = await apiPost('/auth/reset-password/confirm', {
            email: formData.email,
            otp: otpValue,
            new_password: formData.password
          })
          if (!resp?.success) {
            throw new Error(resp?.error || 'Invalid or expired verification code')
          }
          setSuccess('Password updated successfully. Redirecting to login...')
          setTimeout(() => navigate('/login'), 1200)
          return
        } catch (be) {
          setError(be instanceof Error ? be.message : 'Failed to reset password')
          return
        }
      }
      const { error: updateError } = await supabase.auth.updateUser({ password: formData.password })
      if (updateError) {
        setError(updateError.message || 'Failed to update password')
        return
      }
      setSuccess('Password updated successfully. Redirecting to login...')
      setTimeout(() => navigate('/login'), 1200)
    } catch (e) {
      setError('Failed to reset password')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 bg-gray-50">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.4 }}
            className="w-20 h-20 bg-gradient-to-r from-blue-500 to-green-500 rounded-full mx-auto mb-4 flex items-center justify-center"
          >
            <span className="text-white text-2xl font-bold">🔐</span>
          </motion.div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Forgot password</h1>
          <p className="text-gray-600">Reset your password in two quick steps</p>
        </div>

        <div className="flex items-center space-x-4 justify-center mb-6">
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 1 ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-500'}`}>
            <Mail className="h-4 w-4" />
          </div>
          <div className={`w-12 h-1 ${step >= 2 ? 'bg-blue-500' : 'bg-gray-200'}`}></div>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 2 ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-500'}`}>
            <CheckCircle className="h-4 w-4" />
          </div>
        </div>

        <div className="bg-white shadow-lg rounded-2xl p-6">
          {error && (
            <div className="mb-4 p-3 bg-red-50 text-red-600 rounded-md flex items-center gap-2">
              <AlertCircle className="w-4 h-4" />
              <span className="text-sm">{error}</span>
            </div>
          )}
          {success && (
            <div className="mb-4 p-3 bg-green-50 text-green-600 rounded-md flex items-center gap-2">
              <CheckCircle className="w-4 h-4" />
              <span className="text-sm">{success}</span>
            </div>
          )}

          {step === 1 && (
            <div className="space-y-4">
              <label className="block text-sm font-medium text-gray-700">Email address</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="you@example.com"
                  className="block w-full pl-10 pr-3 py-3 border rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors border-gray-300"
                />
              </div>
              <button
                onClick={handleSendCode}
                disabled={isLoading || !validateEmail(formData.email)}
                className={`w-full py-3 px-4 rounded-lg font-medium text-white shadow-sm transition-all ${
                  isLoading || !validateEmail(formData.email)
                    ? 'bg-gray-300 cursor-not-allowed'
                    : 'bg-gradient-to-r from-blue-500 to-green-500 hover:from-blue-600 hover:to-green-600'
                }`}
              >
                {isLoading ? 'Sending…' : 'Send verification code'}
              </button>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Enter verification code</label>
                <div className="flex space-x-2 justify-center">
                  {formData.otp.map((digit, index) => (
                    <input
                      key={index}
                      ref={el => (otpRefs.current[index] = el)}
                      type="text"
                      maxLength={1}
                      value={digit}
                      onChange={(e) => handleOTPChange(index, e.target.value)}
                      onKeyDown={(e) => handleOTPKeyDown(index, e)}
                      onPaste={handleOTPPaste}
                    className="w-12 h-12 text-center text-lg font-semibold border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  ))}
                </div>
                <div className="mt-3 text-center">
                  <button
                    type="button"
                    onClick={handleResend}
                    disabled={resendCooldown > 0 || isLoading}
                  className="text-sm text-blue-600 hover:text-blue-700 disabled:text-gray-400"
                  >
                    {resendCooldown > 0 ? `Resend in ${resendCooldown}s` : 'Resend code'}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">New password</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Lock className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    placeholder="Enter new password"
                    className="block w-full pl-10 pr-12 py-3 border rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors border-gray-300"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                  >
                    {showPassword ? (
                      <EyeOff className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                    ) : (
                      <Eye className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                    )}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Confirm password</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Lock className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    type={showConfirmPassword ? 'text' : 'password'}
                    value={formData.confirmPassword}
                    onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                    placeholder="Re-enter new password"
                    className={`block w-full pl-10 pr-12 py-3 border rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 transition-colors ${
                      passwordsMatch || formData.confirmPassword === ''
                        ? 'focus:ring-blue-500 focus:border-blue-500 border-gray-300'
                        : 'border-red-300 focus:ring-red-500 focus:border-red-500'
                    }`}
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    aria-label={showConfirmPassword ? 'Hide confirm password' : 'Show confirm password'}
                  >
                    {showConfirmPassword ? (
                      <EyeOff className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                    ) : (
                      <Eye className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                    )}
                  </button>
                </div>
                {!passwordsMatch && formData.confirmPassword !== '' && (
                  <p className="mt-2 text-sm text-red-600">Passwords do not match</p>
                )}
              </div>

              <button
                onClick={handleResetPassword}
                disabled={!canSubmit}
                className={`w-full py-3 px-4 rounded-lg font-medium text-white shadow-sm transition-all ${
                  !canSubmit
                    ? 'bg-gray-300 cursor-not-allowed'
                    : 'bg-gradient-to-r from-blue-500 to-green-500 hover:from-blue-600 hover:to-green-600'
                }`}
              >
                {isLoading ? 'Updating…' : 'Reset password'}
              </button>

              <div className="text-center">
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  className="inline-flex items-center gap-2 text-sm text-gray-600 hover:text-gray-800"
                >
                  <ArrowLeft className="w-4 h-4" /> Back
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="mt-6 text-center text-sm text-gray-500">
          <Link to="/login" className="text-blue-600 hover:text-blue-700">Back to login</Link>
        </div>
      </div>
    </div>
  )
}

export default ForgotPassword


