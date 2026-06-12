import 'package:injectable/injectable.dart';
import '../../domain/entities/user.dart';
import '../../domain/repositories/auth_repository.dart';
import '../datasources/auth_remote_datasource.dart';
import '../../../../core/error/exceptions.dart';
import '../../../../core/error/failures.dart';

@LazySingleton(as: AuthRepository)
final class AuthRepositoryImpl implements AuthRepository {
  final AuthRemoteDataSource _remoteDataSource;
  const AuthRepositoryImpl(this._remoteDataSource);

  @override
  AuthResult<({User user, String accessToken})> login({
    required String email,
    required String password,
  }) async {
    try {
      final result = await _remoteDataSource.login(
        email: email,
        password: password,
      );
      return (data: (user: result.user, accessToken: result.accessToken), failure: null);
    } on ServerException catch (e) {
      return (data: null, failure: ServerFailure(e.message, statusCode: e.statusCode));
    } on NetworkException catch (e) {
      return (data: null, failure: NetworkFailure(e.message));
    }
  }

  @override
  AuthResult<void> logout() async {
    return (data: null, failure: null);
  }

  @override
  AuthResult<User> getCurrentUser() async {
    return (data: null, failure: const UnknownFailure('Not implemented'));
  }
}
