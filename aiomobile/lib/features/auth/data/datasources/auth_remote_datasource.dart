import 'package:dio/dio.dart';
import 'package:injectable/injectable.dart';
import '../models/auth_response.dart';
import '../../../../core/error/exceptions.dart';

abstract interface class AuthRemoteDataSource {
  Future<AuthTokenResponse> login({
    required String email,
    required String password,
  });
}

@LazySingleton(as: AuthRemoteDataSource)
final class AuthRemoteDataSourceImpl implements AuthRemoteDataSource {
  final Dio _dio;
  const AuthRemoteDataSourceImpl(this._dio);

  @override
  Future<AuthTokenResponse> login({
    required String email,
    required String password,
  }) async {
    try {
      final response = await _dio.post(
        '/auth/login',
        data: {'email': email, 'password': password},
      );
      return AuthTokenResponse.fromJson(
        response.data as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw ServerException(
        e.response?.data?['detail'] as String? ?? 'Login failed',
        statusCode: e.response?.statusCode,
      );
    }
  }
}
