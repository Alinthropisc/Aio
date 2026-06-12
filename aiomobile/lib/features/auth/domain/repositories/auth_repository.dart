// Repository pattern: abstraction in domain, implementation in data layer
import '../entities/user.dart';
import '../../../../core/error/failures.dart';

typedef AuthResult<T> = Future<({T? data, Failure? failure})>;

abstract interface class AuthRepository {
  AuthResult<({User user, String accessToken})> login({
    required String email,
    required String password,
  });

  AuthResult<void> logout();

  AuthResult<User> getCurrentUser();
}
