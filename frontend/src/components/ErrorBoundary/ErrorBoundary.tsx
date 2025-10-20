import React, { Component } from 'react';
import type { ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by Error Boundary:', error, errorInfo);
    this.setState({
      error,
      errorInfo,
    });
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-red-50 to-red-100 p-6">
          <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
            <div className="flex justify-center mb-4">
              <div className="rounded-full bg-red-100 p-3">
                <svg
                  className="w-8 h-8 text-red-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8v4m0 4v.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
            </div>

            <h1 className="text-2xl font-bold text-center text-gray-800 mb-2">
              Oops! Something went wrong
            </h1>

            <p className="text-center text-gray-600 mb-6">
              We encountered an unexpected error. Please try again or contact support if the problem persists.
            </p>

            {this.state.error && (
              <details className="mb-6 p-3 bg-gray-50 rounded border border-gray-200 text-sm">
                <summary className="cursor-pointer font-semibold text-gray-700 hover:text-gray-900">
                  Error Details
                </summary>
                <div className="mt-3 font-mono text-xs text-red-600 whitespace-pre-wrap break-words">
                  {this.state.error.toString()}
                </div>
                {this.state.errorInfo && (
                  <div className="mt-3 font-mono text-xs text-gray-600 whitespace-pre-wrap break-words">
                    {this.state.errorInfo.componentStack}
                  </div>
                )}
              </details>
            )}

            <button
              onClick={this.handleReset}
              className="w-full bg-emerald-800 hover:bg-emerald-900 text-white font-semibold py-2 px-4 rounded transition-colors duration-200"
            >
              Try Again
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
