import React from 'react';
import { Shield, Download, Trash2, Server, Lock } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';

export default function PrivacyDialog({ open, onOpenChange }) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="w-[95vw] max-w-sm sm:max-w-2xl lg:max-w-4xl max-h-[85vh] overflow-y-auto p-4">
        <DialogHeader>
          <DialogTitle>Privacy Policy</DialogTitle>
        </DialogHeader>

        <div className="space-y-3 sm:space-y-6 mt-2">
          {/* Data Processing Purposes Table */}
          <Card>
            <CardHeader>
              <CardTitle>Data Processing</CardTitle>
            </CardHeader>
            <CardContent>
              {/* Mobile Card Layout */}
              <div className="block sm:hidden space-y-3 px-4">
                <div className="border rounded-lg p-3">
                  <div className="font-medium text-base mb-1">Account Information</div>
                  <div className="text-base text-gray-600 mb-2">
                    E-mail, phone number, preferred language
                  </div>
                  <div className="text-base space-y-0.5">
                    <div>• Sign in and account management</div>
                    <div>• Phone number verification</div>
                    <div>• Set language for UI and AI</div>
                    <div>• Collected at sign-up</div>
                    <div>• Retained until account deletion</div>
                  </div>
                </div>

                <div className="border rounded-lg p-3">
                  <div className="font-medium text-base mb-1">AI Personalization</div>
                  <div className="text-base text-gray-600 mb-2">
                    Role, leadership experience, goals, confidence levels
                  </div>
                  <div className="text-base space-y-0.5">
                    <div>• Provide tips before sessions</div>
                    <div>• Personalize responses during sessions</div>
                    <div>• Provide feedback after sessions</div>
                    <div>• Collected at sign-up</div>
                    <div>• Retained until account deletion</div>
                  </div>
                </div>

                <div className="border rounded-lg p-3">
                  <div className="font-medium text-base mb-1">Voice Recordings</div>
                  <div className="text-base text-gray-600 mb-2">
                    Audio recordings during training sessions
                  </div>
                  <div className="text-base space-y-0.5">
                    <div>
                      • Allows users to review past training sessions by listening to the audio
                      recording
                    </div>
                    <div>• Collected at recording time</div>
                    <div>• Retained for 90 days if consent is given</div>
                    <div>• Deleted permanently and immediately otherwise</div>
                  </div>
                </div>

                <div className="border rounded-lg p-3">
                  <div className="font-medium text-base mb-1">Usage Metrics</div>
                  <div className="text-base text-gray-600 mb-2">
                    Days logged in, training sessions, AI tokens used, ...
                  </div>
                  <div className="text-base space-y-0.5">
                    <div>• Track user progress</div>
                    <div>• Mark achievements</div>
                    <div>• Provide app usage metrics</div>
                    <div>• Collected at various points as the user interacts with the app</div>
                    <div>• Retained until account deletion</div>
                  </div>
                </div>
              </div>

              {/* Desktop Table Layout */}
              <div className="hidden sm:block overflow-x-auto">
                <table className="w-full border-collapse">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-3 pr-4 font-semibold">Personal Data Processed</th>
                      <th className="text-left py-3 font-semibold">Purpose</th>
                      <th className="text-left py-3 font-semibold">Storage Duration</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    <tr>
                      <td className="py-4 pr-4">
                        <div className="font-medium">Account Information</div>
                        <div className="text-base text-gray-600 mt-1">
                          E-mail, phone number, preferred language
                        </div>
                      </td>
                      <td className="py-4 pr-4">
                        <ul className="text-base space-y-1">
                          <li>• Sign in and account management</li>
                          <li>• Phone number verification</li>
                          <li>• Set language for UI and AI</li>
                        </ul>
                      </td>
                      <td className="py-4">
                        <ul className="text-base space-y-1">
                          <li>• Collected at sign-up</li>
                          <li>• Retained until account deletion</li>
                        </ul>
                      </td>
                    </tr>

                    <tr>
                      <td className="py-4 pr-4">
                        <div className="font-medium">AI Personalization</div>
                        <div className="text-base text-gray-600 mt-1">
                          Role, leadership experience, goals, confidence levels
                        </div>
                      </td>
                      <td className="py-4 pr-4">
                        <ul className="text-base space-y-1">
                          <li>• Provide tips before sessions</li>
                          <li>• Personalize responses during sessions</li>
                          <li>• Provide feedback after sessions</li>
                        </ul>
                      </td>
                      <td className="py-4">
                        <ul className="text-base space-y-1">
                          <li>• Collected at sign-up</li>
                          <li>• Retained until account deletion</li>
                        </ul>
                      </td>
                    </tr>

                    <tr>
                      <td className="py-4 pr-4">
                        <div className="font-medium">Voice Recordings</div>
                        <div className="text-base text-gray-600 mt-1">
                          Audio recordings during training sessions
                        </div>
                      </td>
                      <td className="py-4 pr-4">
                        <ul className="text-base space-y-1">
                          <li>
                            • Allows users to review past training sessions by listening to the
                            audio recording
                          </li>
                        </ul>
                      </td>
                      <td className="py-4">
                        <ul className="text-base space-y-1">
                          <li>• Collected at recording time</li>
                          <li>• Retained for 90 days if consent is given</li>
                          <li>• Deleted permanently and immediately otherwise</li>
                        </ul>
                      </td>
                    </tr>

                    <tr>
                      <td className="py-4 pr-4">
                        <div className="font-medium">Usage Metrics</div>
                        <div className="text-base text-gray-600 mt-1">
                          Days logged in, training sessions, AI tokens used, ...
                        </div>
                      </td>
                      <td className="py-4 pr-4">
                        <ul className="text-base space-y-1">
                          <li>• Track user progress</li>
                          <li>• Mark achievements</li>
                          <li>• Provide app usage metrics</li>
                        </ul>
                      </td>
                      <td className="py-4">
                        <ul className="text-base space-y-1">
                          <li>• Collected at various points as the user interacts with the app</li>
                          <li>• Retained until account deletion</li>
                        </ul>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          {/* Security Summary */}
          <Card>
            <CardHeader>
              <CardTitle>
                <div className="flex items-center justify-center gap-2">
                  <Shield className="h-4 w-4 sm:h-5 sm:w-5 text-green-600" />
                  Security & Data Protection
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                <div className="flex items-start gap-3">
                  <Server className="h-4 w-4 sm:h-5 sm:w-5 text-blue-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <h4 className="font-medium text-base sm:text-base">EU-Based Servers</h4>
                    <p className="text-base sm:text-base text-gray-600 mt-1">
                      All data is stored and processed on servers located in the European Union
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <Lock className="h-4 w-4 sm:h-5 sm:w-5 text-green-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <h4 className="font-medium text-base sm:text-base">End-to-End Encryption</h4>
                    <p className="text-base sm:text-base text-gray-600 mt-1">
                      Data is encrypted both in-transit and at-rest for maximum security
                    </p>
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t">
                <h4 className="font-medium mb-2 text-base sm:text-base">
                  External Service Providers
                </h4>
                <div className="text-base sm:text-base text-gray-600 space-y-1">
                  <p>
                    • <strong>Vercel</strong> - EU servers and global CDN (DPA)
                  </p>
                  <p>
                    • <strong>Supabase</strong> - EU servers (DPA)
                  </p>
                  <p>
                    • <strong>Fly.io</strong> - EU servers (DPA)
                  </p>
                  <p>
                    • <strong>GCP</strong> - EU servers (DPA)
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* User Rights */}
          <Card>
            <CardHeader>
              <CardTitle>Your Rights</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 sm:gap-4">
                <div className="flex items-start gap-2 sm:gap-3 p-3 sm:p-4 border rounded-lg">
                  <Trash2 className="h-4 w-4 sm:h-5 sm:w-5 text-red-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <h4 className="font-medium text-base sm:text-base">Account Deletion</h4>
                    <p className="text-base sm:text-base text-gray-600 mt-1">
                      Request permanent deletion of your account and all related data
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-2 sm:gap-3 p-3 sm:p-4 border rounded-lg">
                  <Download className="h-4 w-4 sm:h-5 sm:w-5 text-blue-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <h4 className="font-medium text-base sm:text-base">Data Export</h4>
                    <p className="text-base sm:text-base text-gray-600 mt-1">
                      Request an export of all data we have stored about you
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </DialogContent>
    </Dialog>
  );
}
